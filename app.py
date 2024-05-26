#!/usr/bin/env python3

import aws_cdk as cdk

from medspa_scraper.medspa_scraper_stack import MedspaScraperStack


app = cdk.App()
MedspaScraperStack(app, "MedspaScraperStack")

app.synth()
