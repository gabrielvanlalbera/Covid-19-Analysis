# Model artifacts

The training pipeline writes serialized model artifacts here when it runs. These files are generated from the source data and are intentionally ignored by Git so the repository stays reproducible without committing machine-specific binaries. Recreate them with:

```bash
python src/run_analysis.py --raw-dir data/raw --output-dir data/processed
```
