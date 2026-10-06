+++
title = "Handling Django Authentication Redirects in HTMX Applications"
date = "2025-05-02"
description = "A clean solution for handling Django authentication redirects in HTMX applications, preventing login forms from appearing in the wrong place when sessions expire."
tags = [
    "django",
    "htmx",
    "authentication"
]
+++


When a user’s session expires, an HTMX request can follow Django’s login redirect and swap the login page into the target element. I ran into this recently and used middleware to redirect the whole browser instead.

## What's Going Wrong?

HTMX updates part of a page, but an expired session can cause Django to redirect a request to the login page. The returned login HTML can then appear inside a div or table cell rather than replacing the page.

What we really want is to redirect the whole browser to the login page, and then
bring users right back to where they were after they log in again. Simple idea,
slightly tricky execution.

## Redirect with middleware

This middleware converts HTMX 302 responses into a full-page redirect using `HX-Redirect`. It sets a `next` parameter from the referring page or request path.

```python
from urllib.parse import urlparse


class HtmxAuthRedirectMiddleware:
    """
    Middleware to handle HTMX authentication redirects properly.

    When an HTMX request results in a 302 redirect (typically for authentication),
    this middleware:
    1. Changes the response status code to 204 (No Content)
    2. Adds an HX-Redirect header with the redirect URL
    3. Preserves the original request path in the 'next' query parameter

    This ensures that after authentication, the user is returned to the page
    they were attempting to access, maintaining a seamless UX with HTMX.

    Credits: https://www.caktusgroup.com/blog/2022/11/11/how-handle-django-login-redirects-htmx/
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # HTMX request returning 302 likely is login required.
        # Take the redirect location and send it as the HX-Redirect header value,
        # with 'next' query param set to where the request originated. Also change
        # response status code to 204 (no content) so that htmx will obey the
        # HX-Redirect header value.
        if request.headers.get("HX-Request") == "true" and response.status_code == 302:
            # Determine the next path from referer or current request path
            ref_header = request.headers.get("Referer", "")
            if ref_header:
                referer = urlparse(ref_header)
                next_path = referer.path
            else:
                next_path = request.path

            # Parse the redirect URL
            redirect_url = urlparse(response["location"])

            # Set response status code to 204 for HTMX to process the redirect
            response.status_code = 204

            # Update the "?next" query parameter
            query_params = parse_qs(redirect_url.query)
            query_params["next"] = [next_path]
            new_query = urlencode(query_params, doseq=True)

            # Set the new HX-Redirect header
            response.headers["HX-Redirect"] = f"{redirect_url.path}?{new_query}"

        return response
```

_This middleware is inspired by [this
post](https://www.caktusgroup.com/blog/2022/11/11/how-handle-django-login-redirects-htmx/)
by the caktus group._

## How It Works

The middleware changes a 302 response to 204 so HTMX can process the `HX-Redirect` header. That header redirects the whole browser. The `next` parameter records the path to return to after login.

This applies to all HTMX 302 responses, not just authentication redirects. Add checks if other redirects in your application need different handling.

## Adding This to Your Project

Add the middleware to your Django project and its `MIDDLEWARE` list in `settings.py`:

```python
MIDDLEWARE = [
    # Your other middleware stuff...
    'yourapp.middleware.HtmxAuthRedirectMiddleware',
]
```

Just make sure it comes after Django's authentication middleware in the list - order matters here!

Edits:

2025-05-04: Use `urlparse` and `parse_qs` to securely handle urls. Thanks [Adam Johnson](https://fosstodon.org/@adamchainz/114448835195505930)
