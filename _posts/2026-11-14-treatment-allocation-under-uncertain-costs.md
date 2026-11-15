---
layout: post
title: Treatment allocation under uncertain costs
date: 2026-11-14
description: Who to treat when treatment costs are uncertain.
paper: W584E9VL # Zotero item key: links this post to the paper on /publications/
tags: research
---

_Forthcoming in the Journal of Business & Economic Statistics, with Evan Munro, Hao Sun, Shuyang Du and Stefan Wager. [arXiv](https://arxiv.org/abs/2103.11066)_

Suppose you have a fixed budget for a treatment, such as a scarce medical resource or a marketing discount,
and the cost of treating someone is not known in advance: one patient uses the resource for a day, another for a month;
one customer barely uses a discount, another uses it every week. Who should you treat?

## The rule: rank by priority score

Under a budget constraint, the optimal allocation is a **thresholding rule on a priority score**:
everyone gets a score, and those with higher scores are treated first until the budget runs out.
The score compares the expected benefit of treatment with its expected cost, both conditional on pre-treatment covariates.

## Learning the scores from an experiment

We propose practical methods for learning these priority scores from a randomized trial.
The key observation is a statistical connection to a different problem, learning heterogeneous treatment effects
under endogeneity with an instrumental variable, which lets us reuse tools such as instrumental forests.

{% include figure.liquid loading="eager" path="assets/img/publication_preview/W584E9VL.png" class="img-fluid rounded z-depth-1" zoomable=true %}

<div class="caption">
Simulation with partially predictable costs: gain vs. cost as the budget grows.
Cost-aware methods (instrumental forest, linear parametric) dominate ignoring cost.
</div>
