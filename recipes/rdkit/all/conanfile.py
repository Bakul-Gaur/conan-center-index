from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.microsoft import check_min_vs, is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os

required_conan_version = ">=2.0"


class PackageRDKit(ConanFile):
    name = "rdkit"
    description = "RDKit is a collection of cheminformatics and machine-learning software written in C++ and Python."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rdkit/rdkit"
    topics = ("cheminformatics",)
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    build_requires = "cmake/[>=3.16]"

    rdkit_projects = [
        # "Abbreviations",
        # "Alignment",
        # "CIPLabeler",
        # "Catalogs",
        "ChemReactions",
        "ChemTransforms",
        "ChemicalFeatures",
        "DataStructs",
        "Depictor",
        "Deprotect",
        "Descriptors",
        "DistGeomHelpers",
        "DistGeometry",
        "EigenSolvers",
        "FMCS",
        "FileParsers",
        "FilterCatalog",
        "Fingerprints",
        "ForceField",
        "ForceFieldHelpers",
        "FragCatalog",
        "GeneralizedSubstruct",
        "GenericGroups",
        "GraphMol",
        "InfoTheory",
        "MMPA",
        "MarvinParser",
        "MolAlign",
        "MolCatalog",
        "MolChemicalFeatures",
        "MolDraw2D",
        "MolEnumerator",
        "MolHash",
        "MolInterchange",
        "MolStandardize",
        "MolTransforms",
        "O3AAlign",
        "Optimizer",
        "PartialCharges",
        "RDGeneral",
        "RDGeometryLib",
        "RDStreams",
        "RGroupDecomposition",
        "RascalMCES",
        "ReducedGraphs",
        "RingDecomposerLib",
        # "SLNParse",
        "ScaffoldNetwork",
        "ShapeHelpers",
        "SimDivPickers",
        "SmilesParse",
        "Subgraphs",
        "SubstructLibrary",
        "SubstructMatch",
        "TautomerQuery",
        "Trajectory",
        "coordgen",
        "ga",
        "hc",
        "maeparser"
    ]

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "10",
            "clang": "7",
            "gcc": "7",
            "msvc": "191",
            "Visual Studio": "15",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self.settings.compiler == "clang" and self.settings.compiler.version == "13":
            self.settings.compiler.cppstd = "gnu17"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/[>=1.70]")
        self.requires("catch2/[>=3.7]")
        self.requires("freetype/[>=2.13]")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} can not be built as shared on Visual Studio and msvc.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["RDK_INSTALL_INTREE"] = False
        tc.variables["RDK_BUILD_PYTHON_WRAPPERS"] = False
        tc.variables["RDK_BUILD_CPP_TESTS"] = False
        tc.variables["BOOST_ROOT"] = self.dependencies["boost"].package_folder
        tc.variables["Boost_NO_SYSTEM_PATHS"] = True
        tc.variables["FREETYPE_INCLUDE_DIRS"] = os.path.join(self.dependencies["freetype"].package_folder, "include", "freetype2")
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "rdkit")
        self.cpp_info.set_property("cmake_target_name", "rdkit::rdkit")
        self.cpp_info.includedirs = [os.path.join("include", "rdkit")]

        all_targets = []
        for name in self.rdkit_projects:
            all_targets.append(name)
            all_targets.append(f"{name}_static")

        for target in all_targets:
            self.cpp_info.components[target].set_property("cmake_target_name", f"RDKit::{target}")
            self.cpp_info.components[target].libs = [f"RDKit{target}"]
            self.cpp_info.components[target].includedirs = [os.path.join("include", "rdkit")]

        self.cpp_info.components["rdkit_static"].set_property("cmake_target_name", f"rdkit::rdkit_static")
        self.cpp_info.components["rdkit_static"].libs = [f"RDKit{p}_static" for p in self.rdkit_projects]
        self.cpp_info.components["rdkit_static"].includedirs = [os.path.join("include", "rdkit")]

        self.cpp_info.components["rdkit_shared"].set_property("cmake_target_name", f"rdkit::rdkit_shared")
        self.cpp_info.components["rdkit_shared"].libs = [f"RDKit{p}" for p in self.rdkit_projects]
        self.cpp_info.components["rdkit_shared"].includedirs = [os.path.join("include", "rdkit")]

        self.runenv_info.append_path("LD_LIBRARY_PATH", os.path.join(self.package_folder, "lib"))
