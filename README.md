# VideoLucy
<div align="center"><img src="Figures/github_logo.png" width="900"></div>

We propose **VideoLucy**, a deep memory backtracking framework for long video understanding. Inspired by the human recollection process from coarse to fine, VideoLucy employs a **hierarchical memory structure** with progressive granularity. Through an **agent-based iterative backtracking mechanism**, VideoLucy systematically mines video-wide, question-relevant deep memories until sufficient information is gathered to provide a confident answer. In addition, we introduce **EgoMem**, a **new benchmark for long video understanding**. It is designed to comprehensively evaluate a model's ability to understand complex events that unfold over time and capture fine-grained details in extremely long videos.

More details can be found at our paper [VideoLucy: Deep Memory Backtracking for Long Video Understanding](https://videolucy.github.io/).

## News
* 🔥[2025.10.23] The VideoLucy Demo and EgoMem Benchmark are released. Welcome to use!
* 👍[2025.10.14] Our paper is realsed at [Arxiv](https://arxiv.org/abs/2510.12422).

## Demo
Using the default settings, our VideoLucy employs `Qwen2.5-VL-7B` as the MLLM and `DeepSeek-R1` as the LLM. The former is deployed locally, while the latter is accessed via an API.

For the environment configuration of the former, please refer to the [official Qwen repository](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct).

For LLM API calls, this repository uses the API provided by Volcano Engine by default. Please refer to its [official website](https://console.volcengine.com/ark/) to configure the API and obtain your API key. You can also modify our code to use other APIs for LLM calls.
