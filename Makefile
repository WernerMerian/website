site: clean
	cd generate-html/; python generate-html.py
	cp -r static/* _site/
	@echo "\n----------\nSite généré avec succès !"

serve: site
	python -m http.server -d _site 8080

deploy: site
	zip -r website.zip _site/
clean:
	rm -rf _site website.zip
