
from . import options, tornado, make_app, define

def cli_parameters():
    ## command-list parameters 
    # basics
    define("port", default=8888, help="run on the given port", type=int)
    define("proxy_host", default="metrics-host", help="hostname of site-trusted server running `pmproxy`", type=str)
    define("domain", default="davidson.edu", help="site domain name", type=str)
    
    # mTLS client certificates expected by `pmproxy` running on `proxy-host`
    define("client_cert", default=None, help="client certificate to use when contacting `proxy`", type=str)
    define("client_key", default=None, help="client private-key to use when contacting `proxy`", type=str)
    define("client_ca", default=None, help="trusted CA to use when verifying pmproxy certificate", type=str)

    # mTLS server certificates
    define("cert", default=None, help="server TLS certificate to use", type=str)
    define("key", default=None, help="server private-key", type=str)
    define("ca", default=None, help="trusted CA used to verify clients", type=str)

    # path to ini-style config file providing all required command-line parameters
    #  (tornadoweb.org/en/stable/options.html#tornado.options.OptionParser.parse_config_file)
    define("config", type=str, help="path to config file",
           callback=lambda path: parse_config_file(path, final=False))

    pass # end of the line

def main():
    # set cli arguments
    cli_parameters()
    
    # parse arguments
    tornado.options.parse_command_line()
    
    # handle server certificates if provided
    ssl_options = None
    if options.cert and options.key:
        ssl_options={
            'keyfile': options.key,
            'certfile': options.cert
        }
        if options.ca:
            ssl_options['ca_certs'] = options.ca
            pass
        pass

    # build application
    application = make_app()
    
    # do the thing..
    http_server = tornado.httpserver.HTTPServer(application, ssl_options=ssl_options)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
