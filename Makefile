.PHONY: install serve run build clean

install:
	bundle install

serve:
	bundle exec jekyll serve

run: build
	cd _site && python -m http.server 3000

build:
	bundle exec jekyll build

clean:
	rm -rf _site .jekyll-cache
