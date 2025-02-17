import socket
import sys
import traceback
import os
import mimetypes


def response_ok(body=b"This is a minimal response", mimetype=b"text/plain"):
    """
    returns a basic HTTP response
    Ex:
        response_ok(
            b"<html><h1>Welcome:</h1></html>",
            b"text/html"
        ) ->

        b'''
        HTTP/1.1 200 OK\r\n
        Content-Type: text/html\r\n
        \r\n
        <html><h1>Welcome:</h1></html>\r\n
        '''
    """

    # Implement response_ok
    return b"\r\n".join([b"HTTP/1.1 200 OK", b"Content-Type: " + mimetype, b"", body])


def response_method_not_allowed():
    """Returns a 405 Method Not Allowed response"""

    # Implement response_method_not_allowed
    return b"\r\n".join([b"HTTP/1.1 405 Method Not Allowed", b"Allow: GET"])


def response_not_found():
    """Returns a 404 Not Found response"""

    # Implement response_not_found
    return b"\r\n".join([b"HTTP/1.1 404 Not Found"])


def parse_request(request):
    """
    Given the content of an HTTP request, returns the path of that request.

    This server only handles GET requests, so this method shall raise a
    NotImplementedError if the method of the request is not GET.
    """

    # implement parse_request
    header_components = request.split(' ')
    print("header_components[0] is {}".format(header_components[0]))
    if 'GET' not in header_components[0]:
        print("Not a GET request, raising error!")
        raise NotImplementedError
    else:
        return header_components[1]


def response_path(path):
    """
    This method should return appropriate content and a mime type.

    If the requested path is a directory, then the content should be a
    plain-text listing of the contents with mimetype `text/plain`.

    If the path is a file, it should return the contents of that file
    and its correct mimetype.

    If the path does not map to a real location, it should raise an
    exception that the server can catch to return a 404 response.

    Ex:
        response_path('/a_web_page.html') -> (b"<html><h1>North Carolina...",
                                            b"text/html")

        response_path('/images/sample_1.png')
                        -> (b"A12BCF...",  # contents of sample_1.png
                            b"image/png")

        response_path('/') -> (b"images/, a_web_page.html, make_type.py,...",
                             b"text/plain")

        response_path('/a_page_that_doesnt_exist.html') -> Raises a NameError

    """
    # Code below for constructing paths, regardless of OS
    relative_path = os.path.join("webroot", *path.strip("/").split("/"))

    if os.path.isfile(relative_path):
        # Return the mime type & contents
        mime_type = mimetypes.guess_type(relative_path)[0].encode()
        with open(relative_path, "rb") as f:
            content = f.read()

    elif os.path.isdir(relative_path):
        # Return list of files in dir with mime type text
        mime_type = b"text/plain"
        content = "\n".join(os.listdir(relative_path)).encode()

    # Raise a NameError if the requested content is not present
    # under webroot.
    else:
        raise NameError  # path does not exist

    # Fill in the appropriate content and mime_type give the path.
    # See the assignment guidelines for help on "mapping mime-types", though
    # you might need to create a special case for handling make_time.py
    #
    # If the path is "make_time.py", then you may OPTIONALLY return the
    # result of executing `make_time.py`. But you need only return the
    # CONTENTS of `make_time.py`.

    return content, mime_type


def server(log_buffer=sys.stderr):
    address = ('127.0.0.1', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("making a server on {0}:{1}".format(*address), file=log_buffer)
    sock.bind(address)
    sock.listen(1)

    try:
        while True:
            print('waiting for a connection', file=log_buffer)
            conn, addr = sock.accept()  # blocking
            try:
                print('connection - {0}:{1}'.format(*addr), file=log_buffer)

                request = ''
                while True:
                    data = conn.recv(1024)
                    request += data.decode('utf8')

                    if '\r\n\r\n' in request:
                        break

                print("Request received:\n{}\n\n".format(request))

                # Use parse_request to retrieve the path from the request.
                try:
                    path = parse_request(request)

                    # Use response_path to retrieve the content and the mimetype,
                    # based on the request path.
                    try:
                        content, mime_type = response_path(path)
                        response = response_ok(body=content, mimetype=mime_type)

                    except NameError as e:
                        print("Responding with 404!")
                        response = response_not_found()

                except NotImplementedError as e:
                    print("Responding with 405!")
                    response = response_method_not_allowed()

                conn.sendall(response)
                # If parse_request raised a NotImplementedError, then let
                # response be a method_not_allowed response. If response_path raised
                # a NameError, then let response be a not_found response. Else,
                # use the content and mimetype from response_path to build a 
                # response_ok.
                # response = response_ok(
                #     body=b"Welcome to my web server",
                #     mimetype=b"text/plain"
                # )

            except:
                traceback.print_exc()
            finally:
                print("Closing connection!")
                conn.close()

    except KeyboardInterrupt:
        sock.close()
        return
    except:
        traceback.print_exc()


if __name__ == '__main__':
    server()
    sys.exit(0)


