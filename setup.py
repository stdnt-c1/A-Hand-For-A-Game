from setuptools import setup, Extension
import os

# Define the C++ extension
res_balancer_ext = Extension(
    'res_balancer',
    sources=['resBalancer/res_balancer.cpp'],
    include_dirs=['resBalancer'],
    language='c++',
    extra_compile_args=['/O2'] if os.name == 'nt' else ['-O3', '-fPIC'],
    extra_link_args=['/DLL'] if os.name == 'nt' else ['-shared']
)

setup(
    name='AzimuthControl',
    version='1.0.0',
    description='Hand Gesture Recognition System',
    ext_modules=[res_balancer_ext],
    zip_safe=False,
)
