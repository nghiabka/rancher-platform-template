.PHONY: check render test-sample build-sample

check:
	bin/check-host.sh

render:
	bin/render-gitops.sh

test-sample:
	cd apps/sample-api && python -m pytest

build-sample:
	bin/build-local-sample-api.sh
