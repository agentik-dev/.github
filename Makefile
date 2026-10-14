# The org profile page builds nothing, so it has one target.
# check: the vendored copies match their pinned sums, then the hygiene scan
# finds no hit outside .hygiene-allow (agentik-r1 7.3; packet ruling 1).
.PHONY: check
check:
	shasum -a 256 -c --status scripts/vendored.sha256
	scripts/hygiene
