import datetime
from pyramid.config import Configurator
from pyramid.events import NewRequest
from pyramid.renderers import JSON



def add_cors_headers_response_callback(event):
    def cors_headers(request, response):
        response.headers.update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST,GET,DELETE,PUT,OPTIONS',
            'Access-Control-Allow-Headers': 'Origin, Content-Type, Accept, Authorization',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Max-Age': '1728000',
        })
    event.request.add_response_callback(cors_headers)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)

    def datetime_adapter(obj, request):
        return obj.isoformat()

    json_renderer = JSON()
    json_renderer.add_adapter(datetime.datetime, datetime_adapter)
    config.add_renderer('json', json_renderer)

    config.include('pyramid_mako')
    config.add_subscriber(add_cors_headers_response_callback, NewRequest)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('projects', '/api/projects')
    config.add_route('logs', '/api/projects/:project_id/logs')
    config.add_route('diff', '/api/projects/:project_id/diff/:hash')
    config.scan()
    return config.make_wsgi_app()
