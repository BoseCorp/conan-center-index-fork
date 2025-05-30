from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
import os

required_conan_version = ">=2.1"


class GlewConan(ConanFile):
    name = "glew"
    description = "The GLEW library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://github.com/nigels-com/glew"
    topics = ("glew", "opengl", "wrangler", "loader", "binding")
    license = "MIT"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_egl": [True, False],
        "with_glu": ["mesa-glu", "system"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_egl": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def validate(self):
        if self.options.with_glu == "mesa-glu" and (is_apple_os(self) or self.settings.os == "Windows"):
            raise ConanInvalidConfiguration("mesa-glu only suppported on Linux.")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.with_egl

        if self.options.with_glu == None:
            if is_apple_os(self) or self.settings.os == "Windows":
                self.options.with_glu = "system"
            else:
                self.options.with_glu = "mesa-glu"

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("opengl/system")
        # GL/glew.h includes glu.h.
        if self.options.with_glu == "mesa-glu":
            self.requires("mesa-glu/9.0.3", transitive_headers=True)
        else:
            self.requires("glu/system", transitive_headers=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_UTILS"] = False
        tc.variables["GLEW_EGL"] = self.options.get_safe("with_egl", False)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "build", "cmake"))
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        glewlib_target_name = "glew" if self.options.shared else "glew_s"
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_module_file_name", "GLEW")
        self.cpp_info.set_property("cmake_target_name", "GLEW::GLEW")
        self.cpp_info.set_property("pkg_config_name", "glew")
        self.cpp_info.components["glewlib"].set_property("cmake_module_target_name", "GLEW::GLEW")
        self.cpp_info.components["glewlib"].set_property("cmake_target_name", f"GLEW::{glewlib_target_name}")
        self.cpp_info.components["glewlib"].set_property("pkg_config_name", "glew")

        if self.settings.os == "Windows":
            lib_name = "glew32" if self.options.shared else "libglew32"
        else:
            lib_name = "GLEW"
        if self.settings.build_type == "Debug":
            lib_name += "d"
        self.cpp_info.components["glewlib"].libs = [lib_name]
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.components["glewlib"].defines.append("GLEW_STATIC")
        self.cpp_info.components["glewlib"].requires = ["opengl::opengl"]

        if self.options.with_glu == "mesa-glu":
            self.cpp_info.components["glewlib"].requires.append("mesa-glu::mesa-glu")
        else:
            self.cpp_info.components["glewlib"].requires.append("glu::glu")
