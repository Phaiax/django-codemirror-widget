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
CODEMIRROR_DEFAULT_MODE = getattr(settings, 'CODEMIRROR_DEFAULT_MODE', 'htmlmixed')
CODEMIRROR_DEFAULT_THEME = getattr(settings, 'CODEMIRROR_DEFAULT_THEME', 'default')


class CodeMirrorTextarea(forms.Textarea):
    u"""Textarea widget render with `CodeMirror`

    CodeMirror:
        http://codemirror.net/
    """
    def _media(self):
        return forms.Media(css={'all': self.cssfiles},
                           js=[r"%s/lib/codemirror.js" % CODEMIRROR_PATH, ] + self.jsmedia)
    media = property(_media)

    # What media do we need to get a certain mode?
    mode_mimetype_media_association = {'text/html': ['xml', 'javascript', 'css', 'htmlmixed'],
                                       'htmlmixed': ['xml', 'javascript', 'css', 'htmlmixed']}

    # Some js files have additional stylesheets
    js_files_with_stylesheets = ['dialog', 'simple-hint']

    def __init__(self, attrs=None, mode=None, theme=None, utils=[], additional_configuration={}, additional_css="", additional_js="", ** kwargs):
        u"""Constructor of CodeMirrorTextarea
        @keyword mode: CodeMirror mode attribute (string (for MIME and Mode) or dict (for Mode with options): DEFAULT=settings.CODEMIRROR_DEFAULT_MODE)
        @keyword theme: CodeMirror theme attribute (string or space separated string: DEFAULT=settings.CODEMIRROR_DEFAULT_THEME)
        @keyword utils: List of utils to load from the lib / utils directory. Css Files will be included
        @keyword additional_configuration: Additional Parameters for the JS - Codemirror Constructor. Pay attention to proper escaping
        @keyword additional_css: Css to style this specific editarea. Use $$name$$ as alias for the textareas name
        @keyword additional_js: Js to be executed after CodeMirror.fromTextArea(...). Usefull for defining new modes.
                Use $$id$$ as alias for the textareas id, for example: document.getElementById("$$id$$")
                The Editor object is available as window.$$id$$ in javascript
        Example:
            * - - - - - - - - - - - - - - - - - - - - - - - - - -SETTINGS *
            CODEMIRROR_PATH = r"codemirror"
            # Add codemirror to INSTALLED_APPS for automatic import of static files (collectstatic)
            * - - - - - - - - - - - - - - - - - - - - - - - - - - - -FORM *
            from django import forms
            from codemirror.widgets import CodeMirrorTextarea
            class FileEditForm(forms.Form):
                ## Pay attention:
                ## additional_configuration and mode make different escaping approaches (otherwise js-functions would be
                ## forwarded as strings)
                codemirror = CodeMirrorTextarea(
                        mode='text/html',
                        theme = 'ambiance',
                        utils = ['search', 'searchcursor', 'dialog'],
                        additional_configuration={'lineNumbers': 'true', 'lineWrapping': 'true', 'autofocus': 'true',
                                                    'example_string_property': '"value"',
                                                    'indentUnit': '4', 'onKeyEvent': '''function(editor, event){
                                                        event = $.event.fix(event); // Jquery available
                                                        if (event.type == "keypress" && event.altKey && event.which == 114)
                                                        {
                                                             editor.save();
                                                             $(editor.getTextArea()).parents('form').submit();
                                                             return true;
                                                        }
                                                    }'''}
                        )
                file_content = forms.CharField(widget=codemirror)
                def __init__(self, mode='text/html', *args, **kwargs):
                    super(FileEditForm, self).__init__(*args, **kwargs)
                    ## Update Widget preferences by constructor variables
                    self.fields['file_content'].widget.mode = mode
                    # or for example
                    self.fields['file_content'].widget.mode = {"name": "javascript", "json": True}
                    # you can apply styles to this instance only 
                    self.fields['file_content'].widget.additional_css = '''
                        textarea#$$id$$ ~ .Codemirror .CodeMirror-selected {
                            background-color: blue;
                        }'''
                    # After Changing mode or utils or theme you should call
                    self.fields['file_content'].widget.refresh_media()
            * - - - - - - - - - - - - - - - - - - - - - - - - - - - -TEMPATE *
            Use this in your < head > tags to include the needed media. Maybe use {% block %}.
            {{ form.media.js }}
            {{ form.media.css }}
            * - - - - - - - - - - - - - - - - - - - - - - - - - - USE IN ADMIN *
            # With this code, you can enable the CodeMirrorWidget for each field 
            # in particular
            class SlideAdminForm(forms.ModelForm):
                class Meta:
                    model = Slide
                    cmconfig = {'theme':'ambiance', 'utils' : ['search', 'searchcursor', 'dialog', 'overlay', 'match-highlighter'],
                               'additional_configuration': {'lineNumbers': 'true', 'lineWrapping': 'true', 'autofocus': 'true',
                                                         'indentUnit': '4' }}
                    widgets = {
                        'scriptcode': CodeMirrorTextarea(**cmconfig),
                    }
            
            class SlideAdmin(admin.ModelAdmin):
                form=SlideAdminForm
 
            * - - - - - - - - - - - - - - - - - - - - - - - - - - - -END *

        """
        super(CodeMirrorTextarea, self).__init__(attrs=attrs, **kwargs)
        self.mode = mode or CODEMIRROR_DEFAULT_MODE
        self.theme = theme or CODEMIRROR_DEFAULT_THEME
        self.additional_configuration = additional_configuration
        self.utils = utils
        self.additional_css = additional_css
        self.additional_js = additional_js
        self.refresh_media()

    def refresh_media(self):
        # Mode can be string or dict. For Mimetypes (eg text/html), codemirror can't handle dicts
        if type(self.mode) is list or type(self.mode) is tuple:
            raise ValueError # Lists are no longer supported
        if type(self.mode) is dict:
            self.modename = self.mode['name']
        else:
            self.modename = self.mode

        if self.modename in self.mode_mimetype_media_association.keys():
            self.jsmedia = self.mode_mimetype_media_association[self.modename]
        elif '/' in self.modename:
            raise NotImplementedError("Currently, not all MIME-Types are supported in django-codmirror-widget. Please update" +
            "CodeMirrorTextarea.mode_mimetype_media_association to get your MIME working. Please forward changes upstream.")
        else:
            self.jsmedia = [self.modename]
        self.jsmedia = [settings.STATIC_URL + CODEMIRROR_PATH + '/mode/' + n + "/" + n + ".js" for n in self.jsmedia]

        self.jsmedia = self.jsmedia + [settings.STATIC_URL + CODEMIRROR_PATH + '/lib/util/' + n + ".js" for n in self.utils]

        ## Convert theme to list ...*
        if not hasattr(self.theme, '__iter__'):
            if ' ' in self.theme:
                self.theme = self.theme.split(' ')
            else:
                self.theme = [self.theme, ]
        self.cssfiles = list(self.theme)
        self.cssfiles = [settings.STATIC_URL + CODEMIRROR_PATH + '/theme/' + css + ".css" for css in self.cssfiles if css != 'default']
        self.cssfiles = self.cssfiles + [settings.STATIC_URL + CODEMIRROR_PATH + '/lib/codemirror.css']
        self.cssfiles = self.cssfiles + [settings.STATIC_URL + CODEMIRROR_PATH + '/lib/util/' + n + ".css"
                                         for n in self.utils if n in self.js_files_with_stylesheets]
        ## *... and back to string
        if hasattr(self.theme, '__iter__'):
            self.theme = ' '.join(self.theme)

    def render(self, name, value, attrs=None):
        u"""Render CodeMirrorTextarea"""
        html = super(CodeMirrorTextarea, self).render(name, value, attrs)
        id = 'id_%s' % name
        kwargs = {
            'id': id,
            'mode': json.dumps(self.mode),
            'theme': '"%s"' % (self.theme,),
            'additional_configuration': ",\n\r     ".join(['%s :%s' % i for i in self.additional_configuration.items()]),
            'additional_js': self.additional_js.replace('$$id$$', id),
            'additional_css': self.additional_css.replace('$$id$$', id),
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

