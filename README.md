<div id="top"></div>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/amsen20/Sal">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Sal</h3>

  <p align="center">
    A compiler and VM for Executable Directed Acyclic Graph (EDAG)
  </p>
</div>

<!-- ABOUT THE PROJECT -->
## About The Project

In this project, we are trying to compile arithmetic python codes to Executable Directed Acyclic Graph(EDAG)s and run them as EDAGs.

EDAGs are acyclic so running them in a parallel manner on multiple processors would be much easier compared to normal code.
Also EDAGs are capable of being configured on FPGAs or any other partially reconfigurable hardwares.

Becuase these days common processors are based Von Neuwmann design, Running EDGAs on them will cause some efficiency problems that we are trying
to solve them by partitioning algorithms and precompiling techniques.

### Built With

* [C++(clang)](https://clang.llvm.org/)
* [Python](https://www.python.org/)
* [Cmake](https://cmake.org/)
* [moodycamel::ConcurrentQueue](https://github.com/cameron314/concurrentqueue)

### Prerequisites

* Python (>=3.8)
* Cmake (>=3.21.1)
* C++ (>=17)
* Clang (>=12)

## Usage

* Compiler
  ```sh
  cd compiler
  python3 compiler.py path/to/python/file
  ```
  It generates a sal file named `a.sal`
* VM
  ```sh
  cd vm
  mkdir build
  cd build
  cmake ..
  cmake --build .
  ./salvm path/to/sal/file
  ```
* Input python codes

  For now, the compiler input python file should only contain simple arithmetic functions, recursion is allowed.
  Only integers are allowed for data types.
  There should be a `main` function that will be executed by VM.
  Following code is a simple accepted by compiler fibonacci code:
  ``` python
  def fib(n):
    ret = 1
    if n > 1:
        ret = fib(n-1) + fib(n-2)
    return ret
    
  def main(n):
      return fib(n)
  ```

## Roadmap

- [x] Add compiler
- [x] Add vm
- [x] Add recursion and `if` (after this, vm will be turing complete)
- [ ] Add `List` data type to compiler
- [ ] Add `while` to compiler
- [ ] Fix vm efficiency problems
    - [ ] Add partitioning algorithms
    - [ ] Add precompiling techniques

See the [open issues](https://github.com/othneildrew/Best-README-Template/issues) for a full list of proposed features (and known issues).


## License

Distributed under the MIT License. See `LICENSE.txt` for more information.


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/othneildrew/Best-README-Template.svg?style=for-the-badge
[contributors-url]: https://github.com/othneildrew/Best-README-Template/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/othneildrew/Best-README-Template.svg?style=for-the-badge
[forks-url]: https://github.com/othneildrew/Best-README-Template/network/members
[stars-shield]: https://img.shields.io/github/stars/othneildrew/Best-README-Template.svg?style=for-the-badge
[stars-url]: https://github.com/othneildrew/Best-README-Template/stargazers
[issues-shield]: https://img.shields.io/github/issues/othneildrew/Best-README-Template.svg?style=for-the-badge
[issues-url]: https://github.com/othneildrew/Best-README-Template/issues
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=for-the-badge
[license-url]: https://github.com/amsen20/Sal/blob/main/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/amirhossein-pashaee-a53a44b0/
[product-screenshot]: images/screenshot.png
