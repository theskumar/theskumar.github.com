+++
title = "Efficiently Managing Mass URL Redirects with Nginx"
date = "2017-09-25"
description = "Learn how to implement and manage hundreds of URL redirections efficiently using Nginx's map module and hash maps for optimal server performance"
tags = [
    "devops",
    "nginx",
    "configuration"
]
+++

In this post, I'll show you how to efficiently implement hundreds or even thousands of URL redirects on your server without sacrificing performance. We'll use Nginx's powerful `map` module which creates optimized hash tables for fast lookups.

## Creating Your Redirect Configuration

First, create a file called `redirects-map.conf` where each line represents a single redirect rule in this format:

```text
<old_location> <new_url>;
```

You can use two types of location specifications:

**Simple path redirects**:

```text
/contact-success/ /contact;
```

**Regex-based redirects** (prefixed with `~`):

```text
~^/showcase/(.*)?$ /projects/;
```

Here's an example of a `redirects-map.conf` file:

```nginx
# /etc/nginx/redirects-map.conf

# Simple redirects
/contact-success/ /contact;
/old-page/ /new-page;
/outdated-content/ https://newdomain.com/content;

# Pattern-based redirects
~^/showcase/(.*)?$ /projects/;
~^/articles/(\d+)/(.*)$ /blog/$2;
```

## Configuring Nginx

### Step 1: Upload the configuration
Upload your `redirects-map.conf` to your server at `/etc/nginx/`

### Step 2: Set up the map directive
Add the following at the top of your nginx virtualhost file (outside any server blocks):

```nginx
map $uri $redirected_url {
    default "none";
    include /etc/nginx/redirects-map.conf;
}
```

### Step 3: Add the rewrite rule
Inside your `server` block, add this redirection rule:

```nginx
# Handle redirects defined in the map
if ($redirected_url != "none") {
    rewrite ^ $redirected_url permanent;
}
```

Your complete virtualhost configuration should look something like this:

```nginx
map $uri $redirected_url {
    default "none";
    include /etc/nginx/redirects-map.conf;
}

server {
    listen        443 ssl http2;
    server_name   example.org;

    # Handle redirects defined in the map
    if ($redirected_url != "none") {
        rewrite ^ $redirected_url permanent;
    }

    # Your other server configuration directives
    # ...
}
```

### Step 4: Testing
After saving your changes, test your Nginx configuration:

```bash
nginx -t
```

If successful, reload Nginx:

```bash
nginx -s reload
```

## Handling Large Redirect Sets

> **Important**: Nginx has memory limitations for map files, controlled by the `map_hash_bucket_size` and `map_hash_max_size` directives. If you encounter an error like `[emerg]: could not build the map_hash`, you'll need to increase these values.

Add these directives to the `http` block in your `nginx.conf`:

```nginx
http {
    # Increase these values for large redirect sets
    map_hash_bucket_size 128;  # Default is 32/64 depending on architecture
    map_hash_max_size 4096;    # Default is 2048

    # Rest of your http configuration
    # ...
}
```

For very large redirect sets (e.g., 30KB file), you might need values like:

```nginx
map_hash_bucket_size 256;
map_hash_max_size 30720;
```

## Performance Considerations

The map module is highly efficient because:

1. It uses a hash table for O(1) lookups regardless of how many redirects you have
2. It loads the entire redirect configuration into memory once during startup
3. It avoids the performance penalties of using multiple `if` or `location` blocks

This approach is ideal for sites migrating to new URL structures or consolidating content from multiple domains.
