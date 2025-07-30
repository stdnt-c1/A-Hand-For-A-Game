from setuptools import setup, Extension

res_balancer_module = Extension(
    'res_balancer',
    sources=['res_balancer.cpp'],
    include_dirs=['.'],
    language='cpp',
    extra_compile_args=['-std=c++11']
)

setup(
    name='res_balancer',
    version='1.0',
    description='A performance-critical calculator for AzimuthControl.',
    ext_modules=[res_balancer_module],
)