# Audio File Tools

Use [FFmpeg](https://ffmpeg.org/) to convert WAV audio to MP3 or combine WAV chunks.

## Convert WAV to MP3

```bash
ffmpeg -i input.wav -codec:a libmp3lame -qscale:a 2 output.mp3
```

### Command explanation

- `-i input.wav`: specifies the input file.
- `-codec:a libmp3lame`: encodes the audio using the MP3 encoder.
- `-qscale:a 2`: selects high variable-bitrate quality; lower values mean higher quality.
- `output.mp3`: names the output file.

## Concatenate WAV files

Create a text file (for example, `files.txt`) listing the WAV files in the desired order:

```text
file 'chunk-001.wav'
file 'chunk-002.wav'
file 'chunk-003.wav'
```

Then concatenate them:

```bash
ffmpeg -f concat -safe 0 -i files.txt -c copy combined.wav
```

### Command explanation

- `-f concat`: uses FFmpeg's concat-list format.
- `-safe 0`: allows paths in the list that FFmpeg might otherwise reject as unsafe.
- `-i files.txt`: reads the ordered list of WAV files.
- `-c copy`: joins the files without re-encoding; their audio formats must be compatible.
- `combined.wav`: names the output file.

Stream-copy concatenation requires the WAV files to have matching audio formats. If they do not, let FFmpeg re-encode the result:

```bash
ffmpeg -f concat -safe 0 -i files.txt combined.wav
```

This omits `-c copy`, so FFmpeg re-encodes the combined audio using its default settings. Use this if the WAV files are not compatible for stream-copy concatenation.

Alternatively, [SoX](https://sox.sourceforge.net/) can concatenate WAV files:

```bash
sox chunk-*.wav combined.wav
```

The shell expands `chunk-*.wav` to matching filenames, and SoX joins them in that order. Zero-padded filenames (such as `chunk-002.wav`) help keep the order chronological; otherwise, `chunk-10.wav` may come before `chunk-2.wav`.
