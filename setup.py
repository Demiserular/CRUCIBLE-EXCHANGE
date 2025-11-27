from setuptools import setup, Extension
from pybind11.setup_helpers import Pybind11Extension, build_ext
import sys

ext_modules = [
    Pybind11Extension(
        "crucible_engine",
        ["src/bindings.cpp", "src/matching_engine.cpp"],
        include_dirs=["src"],
        cxx_std=17,
        extra_compile_args=[
            "/O2" if sys.platform == "win32" else "-O3",
            "/std:c++17" if sys.platform == "win32" else "-std=c++17",
        ],
    ),
]

setup(
    name="crucible-engine",
    version="1.0.0",
    author="Crucible Team",
    description="High-performance C++ matching engine for FIX exchange",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.8",
)
