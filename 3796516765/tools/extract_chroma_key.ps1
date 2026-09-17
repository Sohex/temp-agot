param(
	[Parameter(Mandatory = $true)]
	[string]$InputPng,
	[Parameter(Mandatory = $true)]
	[string]$OutputPng
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

$source = [Drawing.Bitmap]::FromFile((Resolve-Path $InputPng))
$output = [Drawing.Bitmap]::new($source.Width, $source.Height, [Drawing.Imaging.PixelFormat]::Format32bppArgb)
try {
	for ($y = 0; $y -lt $source.Height; $y++) {
		for ($x = 0; $x -lt $source.Width; $x++) {
			$pixel = $source.GetPixel($x, $y)
			$other = [Math]::Max([int]$pixel.R, [int]$pixel.B)
			$greenExcess = [Math]::Max(0, [int]$pixel.G - $other)
			$keyFloor = 8
			$keyCeiling = 190
			if ($greenExcess -le $keyFloor) {
				$alpha = 255
			}
			elseif ($greenExcess -ge $keyCeiling) {
				$alpha = 0
			}
			else {
				$alpha = [Math]::Round(255.0 * ($keyCeiling - $greenExcess) / ($keyCeiling - $keyFloor))
			}

			if ($alpha -le 2) {
				$output.SetPixel($x, $y, [Drawing.Color]::Transparent)
				continue
			}

			# Remove green spill only where green actually dominates. Blue jewels and
			# neutral silver pixels keep their original channels unchanged.
			$red = $pixel.R
			$blue = $pixel.B
			$green = if ($greenExcess -gt $keyFloor) { $other } else { $pixel.G }
			$output.SetPixel($x, $y, [Drawing.Color]::FromArgb($alpha, $red, $green, $blue))
		}
	}

	$directory = Split-Path -Parent $OutputPng
	if ($directory -and -not (Test-Path -LiteralPath $directory)) {
		New-Item -ItemType Directory -Path $directory | Out-Null
	}
	$output.Save($OutputPng, [Drawing.Imaging.ImageFormat]::Png)
}
finally {
	$output.Dispose()
	$source.Dispose()
}

Write-Output "Extracted transparent image: $OutputPng"
