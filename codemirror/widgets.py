# -*- coding: utf-8 -*-
#
# Created:    2010/09/09
# Author:         alisue
#
from django import forms
from django.conf import settings
from django.contrib.admin.widgets import AdminTextareaWidget
from django.template.loader import render_to_string
from django.utils import simplejson as json
from django.utils.safestring import mark_safe


# set default settings
CODEMIRROR_PATH = getattr(settings, 'CODEMIRROR_PATH', 'codemirror')
if CODEMIRROR_PATH.endswith('/'):
    CODEMIRROR_PATH = CODEMIRROR_PATH[:-1]
CODEMIRROR_DEFAULT_PARSERFILE = getattr(settings, 'CODEMIRROR_DEFAULT_PARSERFILE', 'parsedummy.js')
CODEMIRROR_DEFAULT_STYLESHEET = getattr(settings, 'CODEMIRROR_DEFAULT_STYLESHEET', '')


class CodeMirrorTextarea(forms.Textarea):
    u"""Textarea widget render with `CodeMirror`

    CodeMirror:
        http://codemirror.net/
    """
    def _media(self):
        self.mode

        return forms.Media(css={'all': self.themepath},
                           js = [r"%s/lib/codemirror.js" % CODEMIRROR_PATH, ] + self.jsmedia)
    media = property(_media)

    def __init__(self, attrs=None, path=None, mode=None, theme=None, additional_configuration={}, ** kwargs):
        u"""Constructor of CodeMirrorTextarea

        Attribute:
            path          - CodeMirror directory URI (DEFAULT = settings.CODEMIRROR_PATH)
            mode - CodeMirror parserfile attribute (string or string array: DEFAULT=settings.CODEMIRROR_DEFAULT_PARSERFILE)
            theme - CodeMirror stylesheet attribute (uri or uri array: DEFAULT=settings.CODEMIRROR_DEFAULT_STYLESHEET)

        Example:
            *-------------------------------*
            + static
              + codemirror
                + css
                  - xmlcolors.css
                + js
                  - codemirror.js
                  - parsexml.js
            *-------------------------------*
            CODEMIRROR_PATH = r"codemirror"

            codemirror = CodeMirrorTextarea(
                # mode='xml',                                # Can be written as the left when only one file is needed.
                mode = {name: "javascript", json: true},
                # theme=r'eclipse'    # Can be written as the left when only one file is needed.
                theme = [r'eclipse'], # Old notation will work too
            )
            document = forms.TextField(widget=codemirror)
        """
        super(CodeMirrorTextarea, self).__init__(attrs=attrs, **kwargs)
        self.path = path or settings.STATIC_URL + CODEMIRROR_PATH + '/lib/'
        self.mode = mode or CODEMIRROR_DEFAULT_PARSERFILE
        self.theme = theme or CODEMIRROR_DEFAULT_STYLESHEET
        self.additional_configuration = additional_configuration

        if hasattr(self.mode, '__iter__'):
            raise ValueError # Lists are no longer supported
        if type(self.mode) is not dict:
            self.mode = {'name': self.mode}

        self.jsmedia = []
        # Raise common error:
        print self.mode
        if self.mode['name'] == 'htmlmixed':
            raise ValueError('See codemirror Dokumentation. You have to use "text/html" instead.')
        # Expand shortterms
        if self.mode['name'] == 'text/html':
            self.jsmedia = self.jsmedia + ['xml', 'javascript', 'css', 'htmlmixed']
        else:
            self.jsmedia = self.jsmedia + [self.mode['name']]

        self.jsmedia = [settings.STATIC_URL + CODEMIRROR_PATH + '/mode/' + n + "/" + n + ".js" for n in self.jsmedia]

        ## Convert theme to list and back to string
        if not hasattr(self.theme, '__iter__'):
            if ' ' in self.theme:
                self.theme = self.theme.split(' ')
            else:
                self.theme = [self.theme, ]
        self.themepath = list(self.theme)
        ## Default theme has got an other path base
        if 'default' in self.theme:
            self.themepath.remove('default')
        self.themepath = [settings.STATIC_URL + CODEMIRROR_PATH + '/theme/' + css + ".css" for css in self.themepath]
        self.themepath = self.themepath + [settings.STATIC_URL + CODEMIRROR_PATH + '/lib/codemirror.css']
        if hasattr(self.theme, '__iter__'):
            self.theme = ' '.join(self.theme)

    def render(self, name, value, attrs=None):
        u"""Render CodeMirrorTextarea"""
        html = super(CodeMirrorTextarea, self).render(name, value, attrs)
        kwargs = {
            'id': '"id_%s"' % name,
            'path': json.dumps(self.path),
            'mode': json.dumps(self.mode),
            'theme': json.dumps(self.theme),
            'additional_configuration': ",\n\r     ".join(['%s :%s' % i for i in self.additional_configuration.items()]),
        }
        for key in kwargs.keys():
            kwargs[key] = mark_safe(kwargs[key])
        code = render_to_string(r"codemirror/javascript.html", kwargs)
        body = "%s\n%s" % (html, code)
        return mark_safe(body)


class AdminCodeMirrorTextareaWidget(CodeMirrorTextarea, AdminTextareaWidget):
    u"""CodeMirrorTextarea for Admin site"""
    pass


class AdminHTMLEditor(AdminCodeMirrorTextareaWidget):
    def __init__(self, *args, **kwargs):
        kwargs['mode'] = ["xml", "css", "javascript", "htmlmixed"]
        kwargs['theme'] = ["xml", "js", "css"]
        super(AdminHTMLEditor, self).__init__(*args, **kwargs)
