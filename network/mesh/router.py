#!/usr/bin/env python3

class Router(object):
    node = None
    routes = []

    def route(self, pattern):
        def wrapper(handler):
            self.routes.append((pattern, handler))
            return handler
        return wrapper

    def recv(self, program, message, interface=None):

        def default_route(program, message=None, interface=None):
            pass

        # Move through routes to find a match to handle a message
        for pattern, handlers in self.routes:
            # if the pattern is a compiled regex try to match it
            if hasattr(pattern, 'match') and pattern.match(message):
                break
            # if pattern is a str, check for a match
            if message == pattern:
                break

        else:
            # if no matches fall back to default route
            handler = default_route

        handler(program, message, interface)
