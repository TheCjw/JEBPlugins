#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: TheCjw<thecjw@live.com>
# Created on 2016.02.03

__author__ = "TheCjw"

from jeb.api import IScript
from jeb.api.ui import View

third_party_packages = """android.
android.support.
cn.jpush
com.actionbarsherlock.
com.alipay.sdk.
com.amap.api.location.
com.baidu.
com.github.
com.google.
com.igexin.
com.j256.ormlite.
com.loopj.android.
com.squareup.okhttp.
com.umeng.
com.weibo.
de.appplant.cordova.
de.greenrobot.event.
javax.annotation.
net.sourceforge.
org.apache.
"""


class Collapse3rdPackages(IScript):
    def run(self, jeb):
        self.jeb = jeb
        self.jebUi = self.jeb.getUI()

        # TODO: for dex: collapse all packages or third party packages.
        #        for apk: collapse all packages first, than expand current package only.

        instance_tree_view = self.jebUi.getView(View.Type.CLASS_HIERARCHY)

        field_real_view = View.getDeclaredField("v")
        field_real_view.setAccessible(True)
        instance_real_view = field_real_view.get(instance_tree_view)

        field_pattern = None
        class_pattern = None
        for field in instance_real_view.getClass().getDeclaredFields():
            if field.getType().getName() == "java.util.regex.Pattern":
                field_pattern = field
                class_pattern = field.getType()
                break

        if field_pattern is None or class_pattern is None:
            print "java.util.regex.Pattern field is not found."
            return

        field_pattern.setAccessible(True)

        method_compile = None
        for method in class_pattern.getMethods():
            if method.getName() == "compile":
                args = 0
                for x in method.getParameterTypes():
                    args += 1
                if args == 1:
                    method_compile = method
                    break

        if method_compile is None:
            print "java.util.regex.Pattern#compile is not found."
            return

        temp = "|".join(third_party_packages.strip().replace(".", "\.").splitlines())
        temp = "^({0}).*".format(temp)
        print temp
        new_pattern = method_compile.invoke(None, temp)

        field_pattern.set(instance_real_view, new_pattern)

        instance_tree_view.refresh()
        print "Done..."
