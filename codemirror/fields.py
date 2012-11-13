'''
Created on 11.11.2012

@author: daniel
'''
from django.db import models
from codemirror.widgets import CodeMirrorTextarea

def integrate_with_south():
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^codemirror\.Fields\.CodeMirrorTextareaField"])
    add_introspection_rules([], ["^codemirror\.Fields\.CommonCodeMirrorTextareaField"])


class CodeMirrorTextareaField(models.TextField):
    def __init__(self, attrs=None, mode=None, theme=None, utils=[], additional_configuration={}, additional_css="", additional_js="", *args, **kwargs):
        u"""
            @keyword all: See Dokumentation of codemirror.widgets.CodeMirrorTextarea  
        """
        self.widget = CodeMirrorTextarea(attrs=attrs, mode=mode, utils=utils, additional_configuration=additional_configuration, additional_css=additional_css, additional_js=additional_js)
        super(CodeMirrorTextareaField, self).__init__(*args, **kwargs)
        
    def formfield(self, **kwargs):
        defaults = {'widget': self.widget}
        defaults.update(kwargs)
        return super(CodeMirrorTextareaField, self).formfield(**defaults)

class CommonCodeMirrorTextareaField(CodeMirrorTextareaField):
    def __init__(self, mode='text/html', intent_unit=4, *args, **kwargs):
        attrs=None
        theme='ambiance'
        utils=['search', 'searchcursor', 'dialog', 'overlay', 'match-highlighter']
        
        additional_configuration={'lineNumbers': 'true',
                                  'lineWrapping': 'true',
                                  'indentUnit': str(intent_unit),
                                  'onCursorActivity': '''
                                            function(editor) {
                                                editor.setLineClass(hlLine, null, null);
                                                hlLine = editor.setLineClass(editor.getCursor().line, null, "activeline");
                                                editor.matchHighlight("CodeMirror-matchhighlight");
                                            }
                                        ''', 'extraKeys': '''
                                            {
                                                "F11": function(cm) {
                                                    setFullScreen(cm, !isFullScreen(cm));
                                                },
                                                "Esc": function(cm) {
                                                    if (isFullScreen(cm)) setFullScreen(cm, false);
                                                }
                                            }
                                        '''}
        additional_js = '''
function isFullScreen(cm) {
    return /CodeMirror-fullscreen/.test(cm.getWrapperElement().className);
}
function winHeight() {
    return window.innerHeight || (document.documentElement || document.body).clientHeight;
}
function setFullScreen(cm, full) {
    var wrap = cm.getWrapperElement(), scroll = cm.getScrollerElement();
    if (full) {
        wrap.className += " CodeMirror-fullscreen";
        scroll.style.height = winHeight() + "px";
        document.documentElement.style.overflow = "hidden";
    } else {
        wrap.className = wrap.className.replace(" CodeMirror-fullscreen", "");
        scroll.style.height = "";
        document.documentElement.style.overflow = "";
    }
    cm.refresh();
}
CodeMirror.connect(window, "resize", function() {
    var showing = document.body.getElementsByClassName("CodeMirror-fullscreen")[0];
    if (!showing) return;
    showing.CodeMirror.getScrollerElement().style.height = winHeight() + "px";
}); 
        
var hlLine = window.$$id$$.setLineClass(0, "activeline");
        '''
        
        additional_css = """
    textarea#$$id$$ ~ .Codemirror .CodeMirror-selected {
        background-color: green;
        opacity: 0.3;
    }
    textarea#$$id$$ ~ .Codemirror {
        
    }
    textarea#$$id$$ ~ .Codemirror:not(.CodeMirror-fullscreen) .CodeMirror-scroll {
        height: auto !important;
        overflow-y: hidden;
        overflow-x: auto;
    }
    textarea#$$id$$ ~ .Codemirror span.CodeMirror-matchhighlight { background: darkgreen; opacity: 0.3; }
    textarea#$$id$$ ~ .Codemirror .CodeMirror-focused span.CodeMirror-matchhighlight { background: darkgreen; opacity: 0.3; !important }
    
    textarea#$$id$$ ~ .CodeMirror-fullscreen, textarea#$$id$$ ~ .Codemirror .CodeMirror-fullscreen {
        display: block;
        left: 0;
        position: absolute;
        top: 0;
        width: 100%;
        z-index: 9999;
    }
    form#editform label {
        display: none;
    }
 
"""
        super(CommonCodeMirrorTextareaField, self).__init__(attrs=attrs, mode=mode, utils=utils, additional_configuration=additional_configuration, additional_css=additional_css, additional_js=additional_js, *args, **kwargs)
        
        