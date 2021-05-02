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
bundle exec jekyll serve
```

Te levanta un servidor local,
al cual podes acceder desde el navegador que más te guste
en `http://localhost:4000`.
