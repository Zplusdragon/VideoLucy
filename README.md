# VideoLucy
<div align="center"><img src="Figures/github_logo.png" width="900"></div>

We propose **VideoLucy**, a deep memory backtracking framework for long video understanding. Inspired by the human recollection process from coarse to fine, VideoLucy employs a **hierarchical memory structure** with progressive granularity. Through an **agent-based iterative backtracking mechanism**, VideoLucy systematically mines video-wide, question-relevant deep memories until sufficient information is gathered to provide a confident answer. In addition, we introduce **EgoMem**, a **new benchmark for long video understanding**. It is designed to comprehensively evaluate a model's ability to understand complex events that unfold over time and capture fine-grained details in extremely long videos.

More details can be found at our paper [VideoLucy: Deep Memory Backtracking for Long Video Understanding](https://videolucy.github.io/).

## News
* 🔥[2025.10.23] The VideoLucy Demo and EgoMem Benchmark are released. Welcome to use!
* 👍[2025.10.14] Our paper is realsed at [Arxiv](https://arxiv.org/abs/2510.12422).

## Demo
By default, our VideoLucy employs `Qwen2.5-VL-7B` as the MLLM and `DeepSeek-R1` as the LLM. The former is deployed locally, while the latter is accessed via an API.

For the environment configuration of the former, please refer to the [official Qwen repository](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct).

For LLM API calls, this repository uses the API provided by Volcano Engine by default. Please refer to its [official website](https://console.volcengine.com/ark/) to configure the API and obtain your API key. You can also modify our code to use other APIs for LLM calls.

Our demo enables downloading videos from the Bilibili platform to local storage and conducting open-ended Q&A dialogues about the downloaded content. To download videos, you need to install the following libraries.

```
pip install you-get
```

Our demo provides a video link along with five questions about the video as a demonstration example.

Video Link:
```
https://www.bilibili.com/video/BV1Y4H6zkE1y
```

Question Examples:
```
1. Which restaurant did the protagonist go to for dinner in the evening? Additionally, in which year was this restaurant established, and what historical background does it have?
2. When the protagonist was eating oysters, how many kinds of sauces were paired with them, and what were they?
3. Where did the protagonist eat the lamb rice bowl? What did this lamb rice bowl look like, and what were its features?
4. Where did the girl the protagonist met while eating on the street come from? What was distinctive about her clothing today?
5. what was the previous profession of the girl the protagonist met while eating by the roadside, and what is her current occupation? What are her comments on the prospects and development of her present career?
```

You need to fill in the `vlm_model_path` and `api_key` in `demo.py`, then run the following command to proceed.
```
python demo.py
```

Note: You can freely modify the `api_model` and `thinking` parameters in the code to specify different LLMs and decide whether to enable reasoning mode. Generally, reasoning mode can provide more accurate responses but may introduce additional inference time. Additionally, you can freely adjust the frame rate and frame count settings in the code to adapt to videos of different durations.

