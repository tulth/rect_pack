# Maintainer: Your Name <youremail@domain.com>
pkgname=python-rect_pack-git
pkgver=10c9a5bd6a86de38b399e295e0552f68b5a51a27
pkgrel=1
pkgdesc=""
arch=(x86_64)
url=""
license=('GPL')
groups=()
depends=('python')
makedepends=()
provides=()
conflicts=()
replaces=()
backup=()
options=(!emptydirs)
install=
source=()
md5sums=()
srcdir=.
pkgdir=pkg.nogit

pkgver() {
  git rev-parse HEAD
}

package() {
  cd $srcdir/..
  python setup.py install --root="$pkgdir/" --optimize=1
}

