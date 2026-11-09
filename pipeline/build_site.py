"""Inline data/hp.json into one offline index.html: python build_site.py pipeline/template.html data/hp.json index.html"""
import sys
t=open(sys.argv[1],encoding="utf-8").read();d=open(sys.argv[2],encoding="utf-8").read().replace("</","<\\/")
open(sys.argv[3],"w",encoding="utf-8").write(t.replace("/*DATA*/",d))
