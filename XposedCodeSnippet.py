#? name=Xposed code snippet, shortcut=Ctrl+Shift+X, author=TheCjw, help=Generate xposed hook code snippet for current method

__author__ = "TheCjw"

from jeb.api import IScript
from jeb.api.ui import View
from jeb.api.dex import Dex

hook_tempplate = """{xposed_method}("{class_name}",
    loadPackageParam.classLoader,
    {method_name}
{params}
    new XC_MethodHook() {{
      @Override
      protected void beforeHookedMethod(MethodHookParam param)
          throws Throwable {{
      }}
      @Override
      protected void afterHookedMethod(MethodHookParam param)
          throws Throwable {{
      }}
    }}
);"""


class XposedCodeSnippet(IScript):
    def __init__(self):
        super(IScript, self).__init__()

    @staticmethod
    def to_canonical_name(dalvik_name):
        dalvik_name = dalvik_name.replace('/', '.')

        type_name = {
            'C': "char",
            'I': "int",
            'B': "byte",
            'Z': "boolean",
            'F': "float",
            'D': "double",
            'S': "short",
            'J': "long",
            'V': "void",
            'L': dalvik_name[1:-1],
            '[': dalvik_name
        }

        return type_name[dalvik_name[0]]

    def run(self, jeb):
        self.jeb = jeb
        self.jebUi = jeb.getUI()
        self.dex = jeb.getDex()

        if not self.jeb.isFileLoaded():
            print "Please load a file"
            return

        code_view = self.jebUi.getView(View.Type.JAVA)
        current_position = code_view.getCodePosition()

        if current_position is None:
            return

        signature = current_position.getSignature()

        if signature.find("(") == -1:
            return

        method_index = self.dex.getMethodData(signature).getMethodIndex()
        dex_method = self.dex.getMethod(method_index)

        method_name = dex_method.getName()
        class_name = XposedCodeSnippet.to_canonical_name(self.dex.getType(dex_method.getClassTypeIndex()))

        if method_name == "<clinit>":
            return

        xposed_method = "findAndHookConstructor" if method_name == "<init>" else "findAndHookMethod"
        method_name = "" if method_name == "<init>" else "\"{0}\",\n".format(method_name)

        proto = self.dex.getPrototype(dex_method.getPrototypeIndex())
        parameters = [XposedCodeSnippet.to_canonical_name(self.dex.getType(i))
                      for i in proto.getParameterTypeIndexes()]

        params = ""
        if len(parameters):
            params = "".join(["    \"{0}\",\n".format(p) for p in parameters])

        lines = hook_tempplate.format(xposed_method=xposed_method,
                                      class_name=class_name,
                                      method_name=method_name,
                                      params=params).splitlines()
        print
        # Remove empty lines.
        print "".join([x + "\n" for x in lines if x.strip()])
        print