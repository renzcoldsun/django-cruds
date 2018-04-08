# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.apps import apps
from django.contrib.auth.decorators import login_required, permission_required

from . import utils
from .views import (
    CRUDCreateView,
    CRUDDeleteView,
    CRUDDetailView,
    CRUDListView,
    CRUDUpdateView,
)


class CrudsUrlValidatorException(Exception):
    def __init__(self, message, errors):
        super(CrudsUrlValidatorException, self).__init__(message)
        self.errors = errors


def create_url_view(view=None, login_reqd=False, permission_reqd=None,
                    login_url=None):
    if view == None:
            raise CrudsUrlValidatorException(u"CRUDS URL VALIDATOR ERROR: \
            View Required \
            ")        
    if login_reqd:
        if permission_reqd != None:
            raise CrudsUrlValidatorException(u"CRUDS URL VALIDATOR ERROR: \
            Login Required and Permission Required cannot be both passed \
            ")
        return login_required(view)
    else:
        if permission_reqd != None:
            if login_url == "" or login_url == None:
                raise CrudsUrlValidatorException(u"CRUDS URL VALIDATOR \
                    ERROR: Permission Required requires login_url \
            ")
            return permission_required(permission_reqd,
                                       login_url=login_url)(view)
        else:
            return view

def crud_urls(model,
              list_view=None,
              create_view=None,
              update_view=None,
              detail_view=None,
              delete_view=None,
              url_prefix=None,
              name_prefix=None,
              list_views=None,
              login_reqd=False,
              permission_reqd=None,
              login_url='login',
              **kwargs):
    """Returns a list of url patterns for model.

    :param list_view:
    :param create_view:
    :param update_view:
    :param detail_view:
    :param delete_view:
    :param url_prefix: prefix to prepend, default is `'$'`
    :param name_prefix: prefix to prepend to name, default is empty string
    :param list_views(dict): additional list views
    :param **kwargs: additional detail views
    :returns: urls
    """
    if url_prefix is None:
        url_prefix = r'^'
    urls = []
    if list_view:
        urls.append(url(
            url_prefix + '$',
            create_url_view(list_view, login_reqd, permission_reqd, login_url),
            name=utils.crud_url_name(model, utils.ACTION_LIST,
                                     name_prefix)
        ))
    if create_view:
        urls.append(url(
            url_prefix + r'new/$',
            create_url_view(create_view, login_reqd, permission_reqd,
                            login_url),
            #create_view,
            name=utils.crud_url_name(model, utils.ACTION_CREATE, name_prefix)
        ))
    if detail_view:
        urls.append(url(
            url_prefix + r'(?P<pk>\d+)/$',
            create_url_view(detail_view, login_reqd, permission_reqd,
                            login_url),
            #detail_view,
            name=utils.crud_url_name(model, utils.ACTION_DETAIL, name_prefix)
        ))
    if update_view:
        urls.append(url(
            url_prefix + r'(?P<pk>\d+)/edit/$',
            create_url_view(update_view, login_reqd, permission_reqd,
                            login_url),
            #update_view,
            name=utils.crud_url_name(model, utils.ACTION_UPDATE, name_prefix)
        ))
    if delete_view:
        urls.append(url(
            url_prefix + r'(?P<pk>\d+)/remove/$',
            create_url_view(delete_view, login_reqd, permission_reqd,
                            login_url),
            #delete_view,
            name=utils.crud_url_name(model, utils.ACTION_DELETE, name_prefix)
        ))

    if list_views is not None:
        for name, view in list_views.items():
            urls.append(url(
                url_prefix + r'%s/$' % name,
                create_url_view(view, login_reqd, permission_reqd,
                                login_url),
                #view,
                name=utils.crud_url_name(model, name, name_prefix)
            ))

    for name, view in kwargs.items():
        urls.append(url(
            url_prefix + r'(?P<pk>\d+)/%s/$' % name,
            create_url_view(view, login_reqd, permission_reqd,
                            login_url),
            #view,
            name=utils.crud_url_name(model, name, name_prefix)
        ))
    return urls


def crud_for_model(model, urlprefix=None, login_rqd=False, perm_rqd=None,
                   login_url=None):
    """Returns list of ``url`` items to CRUD a model.
    """
    model_lower = model.__name__.lower()

    if urlprefix is None:
        urlprefix = ''
    urlprefix += model_lower + '/'

    urls = crud_urls(
        model,
        list_view=CRUDListView.as_view(model=model),
        create_view=CRUDCreateView.as_view(model=model),
        detail_view=CRUDDetailView.as_view(model=model),
        update_view=CRUDUpdateView.as_view(model=model),
        delete_view=CRUDDeleteView.as_view(model=model),
        url_prefix=urlprefix,
        login_reqd=login_rqd,
        permission_reqd=perm_rqd,
        login_url=login_url
    )
    return urls


def crud_for_app(app_label, urlprefix=None, login_rqd=False, perm_rqd=None,
                   login_url=None):
    """
    Returns list of ``url`` items to CRUD an app.
    """
    if urlprefix is None:
        urlprefix = app_label + '/'
    app = apps.get_app_config(app_label)
    urls = []
    for model in app.get_models():
        urls += crud_for_model(model, urlprefix, login_rqd, perm_rqd,
                               login_url)
    return urls

