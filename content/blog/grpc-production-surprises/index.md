+++
title = "Three Things That Bite You When You Ship gRPC to Production"
date = "2026-07-24"
description = "Three things about gRPC that look fine in tutorials and bite you in production: load balancer imbalance, browser incompatibility, and silent schema corruption."
tags = [
    "api-design",
    "backend",
    "infrastructure",
]
toc = false
+++

I recently spent some time going deeper into gRPC, past the quickstart and into HTTP/2 framing, Protobuf encoding, and the parts of the system that sit around the service itself. I came away liking it. Contract-first APIs are useful, generated clients remove an entire class of mistakes, and streaming is part of the protocol rather than something attached later.

I also came away with a list of things I wish the quickstart had made harder to miss. They are not obscure bugs, and they are not arguments against gRPC. They are direct consequences of the choices that make it good.

That is what makes them dangerous.

## Connections Are Not Requests

For a long time I carried a simple model of load balancing: a request arrives, the load balancer picks a backend, and the backend handles it. That model is often close enough for HTTP/1.1 systems, even though the machinery underneath is balancing TCP connections rather than individual requests.

gRPC makes the difference visible. It usually keeps an HTTP/2 connection open and carries many concurrent RPCs over that connection as streams. Reusing the connection avoids handshakes and lets several calls make progress at once. This is one of the reasons gRPC performs well.

An L4 load balancer cannot see those streams. It sees one TCP connection, chooses one backend when that connection opens, and keeps sending the connection there for its lifetime. If a client resolves a single virtual IP and holds one long-lived connection to it, hundreds or thousands of calls can remain pinned to one backend while other instances have very little to do.

The metrics look absurd: one pod is hot, several pods are quiet, and adding more pods changes almost nothing. The cluster has capacity, but the client has no path to it.

It is like assigning a delivery truck to a warehouse when it leaves the depot, then insisting that every package on that truck go to the same warehouse. Adding warehouses does not help. The decision was already made at the wrong level.

The fix is to balance one level higher. A gRPC client can resolve individual backends, keep subchannels to them, and choose one for each RPC with a policy such as `round_robin`. In Kubernetes that often means a headless service rather than a normal ClusterIP service. An HTTP/2-aware proxy such as Envoy, or a service mesh built around one, can also distribute streams across backend connections.

Both approaches work, and both add something I now have to operate: endpoint discovery and health checking in the client, or another proxy in the request path. That may be a good trade. It is still a trade.

A load balancer that understands connections does not necessarily understand gRPC.

## Browser HTTP/2 Is Not gRPC

I made what seemed like an obvious inference: gRPC uses HTTP/2, browsers support HTTP/2, therefore browser JavaScript can call a gRPC service.

It cannot, at least not as native gRPC through the browser APIs available to application code.

The browser may speak HTTP/2 on the network, but JavaScript does not control that connection as an HTTP/2 peer. gRPC places its final status and error details in trailing headers after the response body, and `fetch` and `XMLHttpRequest` do not give application code the trailer behavior native gRPC expects. Client streaming and bidirectional streaming also need the request and response to remain active together, with the client writing while it reads. Browser request APIs have historically not offered that form of full-duplex transport in a portable way.

The browser owns the connection. My code gets a window into it, not the keys.

grpc-web exists to bridge that boundary. It adapts the protocol so trailers can travel inside the response body as a marked frame that browser code can read. A proxy such as Envoy commonly translates between grpc-web on the browser side and native gRPC on the service side, although some servers support grpc-web directly. Unary calls work, and server streaming can work, but client and bidirectional streaming remain constrained by the browser transport.

Connect takes a different approach. A Connect server can expose browser-friendly HTTP alongside gRPC and grpc-web, with JSON or Protobuf payloads, and the browser can call it with ordinary `fetch`. That removes a dedicated translation proxy in many deployments and makes a service much easier to inspect with tools such as `curl`. It does not grant JavaScript arbitrary control over the browser's HTTP/2 connection; available streaming modes still depend on the browser transport.

I do not consider this a flaw in gRPC. It was designed primarily for environments where both ends are programs with control over their network stack, and server-to-server RPC is where its tradeoffs make the most sense. A browser is someone else's runtime, with someone else's security model and someone else's API surface.

The mistake is not that gRPC has a boundary. The mistake is drawing an architecture diagram that pretends the boundary is not there.

## Field Numbers Never Forget

Protobuf field names are for people. Field numbers are for the wire.

```protobuf
message User {
  string name = 1;
  string email = 2;
}
```

The encoded message does not contain the words `name` or `email`. It contains field numbers, wire types, and values. Renaming `name` to `full_name` while keeping field number 1 does not change the wire contract. Changing the number does.

This is easy to understand while looking at one version of a `.proto` file. It becomes harder after field 2 was deleted two years ago, the person who deleted it has moved to another team, and the current file makes number 2 look pleasantly unused.

It is not unused. It is retired.

Suppose a later version reuses field 2 for another length-delimited value:

```protobuf
message User {
  string name = 1;
  bytes avatar_hash = 2; // reused field number
}
```

An old client can still send an email address in field 2. The new server sees the same field number and a compatible wire type, and accepts those bytes as `avatar_hash`. Protobuf cannot object because the old meaning is not present on the wire. Unless validation catches it, perfectly valid bytes can acquire the wrong meaning and travel further into the system.

That is worse than a failed decode.

The fix is a tombstone:

```protobuf
message User {
  reserved 2;
  reserved "email";

  string name = 1;
  bytes avatar_hash = 3;
}
```

`reserved` tells the compiler that the number and name may not be used again. It turns historical knowledge into a rule the tooling can enforce. Without it, the only thing protecting the schema is memory, and organizational memory is not a compatibility mechanism.

The rest of the discipline follows from the same fact. I do not renumber fields. I reserve every removed number and name. I prefer additive changes while old and new binaries must coexist, and I introduce a new message or RPC when the meaning genuinely needs to break. Proto3's removal of `required` fields came from the same hard-earned lesson: one service should not make every older peer invalid merely by evolving its schema.

A field number is small, but it is permanent.

## The Abstraction Ends Somewhere

These three problems looked unrelated to me at first. One was about Kubernetes, one about browsers, and one about schema files. The common thread is that gRPC's guarantees stop at the layer that understands them.

A TCP load balancer does not understand HTTP/2 streams. Browser JavaScript does not control the browser's HTTP/2 implementation. Protobuf understands field numbers and wire types, but it does not understand that some bytes used to mean an email address and now mean an avatar hash.

Put those boundaries together and gRPC becomes less forgiving than its clean interface suggests. The generated method call may look like a local function, but it still crosses a network, a load balancer, a runtime, and a schema history. Every one of those layers gets a vote.

I still like gRPC, especially for internal communication across services written in different languages. The contract is real, the tooling is mature, and native streaming is valuable. I do not want to give those things up merely because the surrounding system needs care.

But I also do not want the elegance of the method call to hide the machinery underneath it. The abstraction is useful only while I remember where it ends.
