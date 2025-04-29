# Web ComCom
Proyecto de la web de la ComCom

## Instalación

Vas a necesitar rbenv.
La instalación dependerá de tu sistema operativo.
A partir de ahí, pararse en el directorio del proyecto y hacer:

```
sudo apt get install rbenv
mkdir -p "$(rbenv root)"/plugins
git clone https://github.com/rbenv/ruby-build.git "$(rbenv root)"/plugins/ruby-build

rbenv init
gem install bundler
bundle install
```

## Correr local

Para correr la página en tu compu, hacé

```
bundler exec jekyll build && bash -c 'cd _site && python -m http.server 3000'

```

Te levanta un servidor local,
al cual podes acceder desde el navegador que más te guste
en `http://localhost:4000`.

## Problemas comunes

### Error largo con referencias a ruby 3

Puede pasar que tengas instalado globalmente Ruby 3 y esté usando ese en vez del de rbenv.
Fijate de agregar rbenv al PATH (editando ~/.bashrc, ~/.zshrc o el archivo que corresponda para tu sistema y consola):

```
export PATH="$HOME/.rbenv/bin:$PATH"
```
