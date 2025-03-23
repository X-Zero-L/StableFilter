# StableFilter

English | [简体中文](README.md)

StableFilter is a tool for intelligent classification of Stable Diffusion model tags. It automatically categorizes tags into different safety levels and provides detailed Chinese explanations and translations.

## Features

- Smart Tag Classification: Categorizes tags into four safety levels: general, sensitive, nsfw, and explicit
- Concurrent Processing: Supports high-concurrency processing of large tag sets
- Resume Capability: Supports resuming from interruptions
- Detailed Explanations: Provides detailed Chinese explanations for each classification
- Chinese Translation: Offers accurate Chinese translations

## Installation

1. Clone the repository:

```bash
git clone https://github.com/X-Zero-L/StableFilter.git
cd StableFilter
```

2. Install dependencies:

```bash
uv sync
```

3. Configure environment variables:

```bash
cp .env.example .env
# Edit the .env file with necessary configuration information
```

## Usage

If you only want to use the pre-classified tag data, you can download it from the releases page of this project.

1. Prepare tag data:
   - Place the tags to be classified in the `selected_tags.csv` file
   - The CSV file should contain a `name` column

2. Run the classification program:

```bash
uv run -m src.main
```

3. View results:
   - Classification results will be saved in `results/tag_classifications.json`
   - You can interrupt the program at any time, and it will automatically resume processing unfinished tags on the next run

## Project Structure

```
StableFilter/
├── src/
│   ├── core/           # Core functionality implementation
│   ├── models/         # Data model definitions
│   ├── utils/          # Utility functions
│   └── config/         # Configuration files
├── tests/              # Test cases
├── docs/               # Documentation
├── results/            # Output directory
└── tag_groups/         # Tag group data
```

## License

MIT License 