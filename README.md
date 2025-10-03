# MigGPT
Official implementation of the paper "MigGPT: Harnessing Large Language Models for Automated Migration of Out-of-Tree Linux Kernel Patches Across Versions" (NeurIPS 2025 spotlight)


## Abstract
Out-of-tree kernel patches are essential for adapting the Linux kernel to new hardware or enabling specific functionalities. Maintaining and updating these patches across different kernel versions demands significant effort from experienced engineers. Large language models (LLMs) have shown remarkable progress across various domains, suggesting their potential for automating out-of-tree kernel patch migration. 
However, our findings reveal that LLMs, while promising, struggle with incomplete code context understanding and inaccurate migration point identification. In this work, we propose MigGPT, a framework that employs a novel code fingerprint structure to retain code snippet information and incorporates three meticulously designed modules to improve the migration accuracy and efficiency of out-of-tree kernel patches. Furthermore, we establish a robust benchmark using real-world out-of-tree kernel patch projects to evaluate LLM capabilities. 
Evaluations show that MigGPT significantly outperforms the direct application of vanilla LLMs, achieving an average completion rate of 74.07\% (↑ 45.92%) for migration tasks.

## Setup: Create and Activate the Environment
1. Create a new Conda environment named miggpt with Python 3.9 installed. Install all necessary packages listed in the requirements.txt file by running:
```
conda create -n miggpt python=3.9
conda activate miggpt
pip install -r requirements.txt
```

2. Configure your OpenAI key in `utils.py`
```
openai.api_key = "your key"
```

## Benchmark
The benchmark file, located at `data/data.csv`, contains 80 Type 1 samples and 55 Type 2 samples. The specific content of each item is as follows:
```
'type',             # Type of migration sample, "type1" or "type2"
's_old',            # Old code snippet
's_old_p',          # Patched old code snippet
'file_new',         # New version file
's_new_gt1',        # Correct result for the new code snippet on retrieval task
's_new_gt2',        # Additional correct result for the new code snippet on the retrieval task
's_new_p_gt1',      # Correct result for patched new code snippet on migration task
's_new_p_gt2'       # Additional correct result for patched new code snippet on migration task
```

## Usage
1. Retrieve the new code snippet from the new version file.
```
python retrieve.py --llm gpt-4-turbo --method miggpt
```
2. Migrate the new code snippet to the patched new code snippet.
```
python migrate.py --llm gpt-4-turbo --method miggpt
```
3. Evaluate the results
```
python evaluate.py --metric best --method miggpt     # Best match
python evaluate.py --metric semantic --method miggpt     # Semantic match
```

## BibTeX
Please cite the paper: 
```
@article{dang2025miggpt,
  title={MigGPT: Harnessing Large Language Models for Automated Migration of Out-of-Tree Linux Kernel Patches Across Versions},
  author={Dang, Pucheng and Huang, Di and Li, Dong and Chen, Kang and Wen, Yuanbo and Guo, Qi and Hu, Xing and Sun, Ninghui},
  journal={arXiv preprint arXiv:2504.09474},
  year={2025}
}
```
