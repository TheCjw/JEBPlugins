# Xposed code snippet for JEB 3.x 

from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit

hook_tempplate = """
{xposed_method}("{class_name}",
    loadPackageParam.classLoader,
    {method_name}
{signatures}
    new XC_MethodHook() {{
      @Override
      protected void beforeHookedMethod(MethodHookParam param)
          throws Throwable {{
{variables}
      }}
      @Override
      protected void afterHookedMethod(MethodHookParam param)
          throws Throwable {{
{variables}
      }}
    }});
"""

class XposedCodeSnippet(IScript):

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

    def run(self, ctx):
        prj = ctx.getMainProject()
        dex = prj.findUnit(IDexUnit)

        if not dex:
            print('[XposedCodeSnippet] Open a DEX unit.')
            return

        addr = ctx.getFocusedView().getActiveFragment().getActiveAddress()

        if not addr:
            print('[XposedCodeSnippet] Invalid address.')
            return

        pos = addr.find('+')
        if pos >= 0:
            mname = addr[0:pos]
            off = int(addr[pos + 1:].rstrip('h'), 16)
        else:
            mname = addr
            off = 0

        _method = dex.getMethod(mname)
        if not _method:
            print('[XposedCodeSnippet] No method found at address: %s' % addr)
            return

        method_name = _method.getName()

        print('[XposedCodeSnippet] Method: %s, Offset: 0x%X' % (mname, off))
        if method_name == "<clinit>":
            return
        
        class_name = XposedCodeSnippet.to_canonical_name(_method.getClassType().address)
        xposed_method = "findAndHookConstructor" if method_name == "<init>" else "findAndHookMethod"
        method_name = "" if method_name == "<init>" else "\"{0}\",\n".format(method_name)

        signatures = ""
        variables = ""
        if len(_method.getParameterTypes()):
            types = [XposedCodeSnippet.to_canonical_name(_param.address) for _param in _method.getParameterTypes()]
            signatures = "".join(["    \"{0}\",\n".format(t) for t in types])
            variables = "".join(["        Object arg{0} = param.args[{1}]; // {2}\n".format(i, i, types[i])
                                 for i in xrange(0, len(types))])

        lines = hook_tempplate.format(xposed_method=xposed_method,
                                      class_name=class_name,
                                      method_name=method_name,
                                      signatures=signatures,
                                      variables=variables).splitlines()
        print("\n")
        print("".join([x + "\n" for x in lines if x.strip()]))
        print("\n")
