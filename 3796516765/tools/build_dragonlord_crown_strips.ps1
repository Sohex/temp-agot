param(
	[string]$SourcePng = (Join-Path $PSScriptRoot '..\art_source\dragonlord_crown_master_v6.png'),
	[string]$ModRoot = (Resolve-Path (Join-Path $PSScriptRoot '..'))
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

function Import-UncompressedDds {
	param([string]$Path)

	$bytes = [System.IO.File]::ReadAllBytes($Path)
	if ([System.Text.Encoding]::ASCII.GetString($bytes, 0, 4) -ne 'DDS ') {
		throw "Not a DDS file: $Path"
	}

	$height = [BitConverter]::ToInt32($bytes, 12)
	$width = [BitConverter]::ToInt32($bytes, 16)
	$bitsPerPixel = [BitConverter]::ToInt32($bytes, 88)
	if ($bitsPerPixel -ne 32 -or $bytes.Length -ne (128 + $width * $height * 4)) {
		throw "Expected an uncompressed 32-bit DDS: $Path"
	}

	$bitmap = [Drawing.Bitmap]::new($width, $height, [Drawing.Imaging.PixelFormat]::Format32bppArgb)
	$rect = [Drawing.Rectangle]::new(0, 0, $width, $height)
	$data = $bitmap.LockBits($rect, [Drawing.Imaging.ImageLockMode]::WriteOnly, [Drawing.Imaging.PixelFormat]::Format32bppArgb)
	try {
		[Runtime.InteropServices.Marshal]::Copy($bytes, 128, $data.Scan0, $width * $height * 4)
	}
	finally {
		$bitmap.UnlockBits($data)
	}

	return [PSCustomObject]@{ Bytes = $bytes; Bitmap = $bitmap }
}

function Export-UncompressedDds {
	param(
		[byte[]]$OriginalBytes,
		[Drawing.Bitmap]$Bitmap,
		[string]$Path
	)

	$pixelBytes = New-Object byte[] ($Bitmap.Width * $Bitmap.Height * 4)
	$rect = [Drawing.Rectangle]::new(0, 0, $Bitmap.Width, $Bitmap.Height)
	$data = $Bitmap.LockBits($rect, [Drawing.Imaging.ImageLockMode]::ReadOnly, [Drawing.Imaging.PixelFormat]::Format32bppArgb)
	try {
		[Runtime.InteropServices.Marshal]::Copy($data.Scan0, $pixelBytes, 0, $pixelBytes.Length)
	}
	finally {
		$Bitmap.UnlockBits($data)
	}

	$output = New-Object byte[] $OriginalBytes.Length
	[Array]::Copy($OriginalBytes, 0, $output, 0, 128)
	[Array]::Copy($pixelBytes, 0, $output, 128, $pixelBytes.Length)
	[System.IO.File]::WriteAllBytes($Path, $output)
}

$source = [Drawing.Bitmap]::FromFile((Resolve-Path $SourcePng))
try {
	$minX = $source.Width
	$minY = $source.Height
	$maxX = -1
	$maxY = -1
	for ($y = 0; $y -lt $source.Height; $y += 2) {
		for ($x = 0; $x -lt $source.Width; $x += 2) {
			if ($source.GetPixel($x, $y).A -gt 5) {
				$minX = [Math]::Min($minX, $x)
				$minY = [Math]::Min($minY, $y)
				$maxX = [Math]::Max($maxX, $x)
				$maxY = [Math]::Max($maxY, $y)
			}
		}
	}
	if ($maxX -lt 0) { throw 'The crown source contains no visible pixels.' }

	$sourceRect = [Drawing.Rectangle]::new($minX, $minY, $maxX - $minX + 1, $maxY - $minY + 1)
	$targets = @(
		# The crown is 20% smaller than v4. BaselineOffset intentionally clips
		# only the lowest soft shadow, putting the visible metal rim against the
		# shield instead of leaving a black gap below it.
		@{ Size = 28; Width = 24; Height = 13; BaselineOffset = 1 },
		@{ Size = 44; Width = 36; Height = 20; BaselineOffset = 1 },
		@{ Size = 62; Width = 46; Height = 26; BaselineOffset = 2 },
		@{ Size = 86; Width = 70; Height = 41; BaselineOffset = 3 },
		@{ Size = 115; Width = 89; Height = 52; BaselineOffset = 4 }
	)

	foreach ($target in $targets) {
		$path = Join-Path $ModRoot "gfx\interface\coat_of_arms\dragonlord_crown_strip_$($target.Size).dds"
		$dds = Import-UncompressedDds -Path $path
		try {
			$frameWidth = [int]($dds.Bitmap.Width / 7)
			$frameIndex = 3
			$frameRect = [Drawing.Rectangle]::new($frameIndex * $frameWidth, 0, $frameWidth, $dds.Bitmap.Height)
			$targetX = $frameRect.X + [int][Math]::Floor(($frameWidth - $target.Width) / 2)
			$targetY = $dds.Bitmap.Height - $target.Height + $target.BaselineOffset
			$targetRect = [Drawing.Rectangle]::new($targetX, $targetY, $target.Width, $target.Height)

			$graphics = [Drawing.Graphics]::FromImage($dds.Bitmap)
			try {
				$graphics.CompositingMode = [Drawing.Drawing2D.CompositingMode]::SourceCopy
				$graphics.FillRectangle([Drawing.Brushes]::Transparent, $frameRect)
				$graphics.InterpolationMode = [Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
				$graphics.PixelOffsetMode = [Drawing.Drawing2D.PixelOffsetMode]::HighQuality
				$graphics.DrawImage($source, $targetRect, $sourceRect, [Drawing.GraphicsUnit]::Pixel)
			}
			finally {
				$graphics.Dispose()
			}

			# Keep the crown's established size and baseline, but make the existing
			# dark surround read like the recessed gutter around vanilla crowns.
			# Only transparent/low-alpha edge pixels are touched: the metal, jewels
			# and silhouette itself are never rescaled or shifted.
			$frameAlpha = New-Object byte[] ($frameRect.Width * $frameRect.Height)
			for ($y = $frameRect.Top; $y -lt $frameRect.Bottom; $y++) {
				for ($x = $frameRect.Left; $x -lt $frameRect.Right; $x++) {
					$pixel = $dds.Bitmap.GetPixel($x, $y)
					$frameAlpha[($y - $frameRect.Top) * $frameRect.Width + ($x - $frameRect.Left)] = $pixel.A
					if ($pixel.A -gt 0 -and $pixel.A -le 140 -and (($pixel.R + $pixel.G + $pixel.B) / 3) -le 48) {
						$shadowAlpha = [Math]::Min(220, [int]([Math]::Round($pixel.A * 1.65)))
						$dds.Bitmap.SetPixel($x, $y, [Drawing.Color]::FromArgb($shadowAlpha, 0, 0, 0))
					}
					elseif ($pixel.A -gt 0 -and $pixel.A -le 8) {
						# Prevent saturated RGB fringe in the non-premultiplied DDS path.
						$dds.Bitmap.SetPixel($x, $y, [Drawing.Color]::FromArgb($pixel.A, 0, 0, 0))
					}
				}
			}

			# One narrow outer shadow pass gives the crown a crisp recessed edge
			# without increasing the visible crown's dimensions.
			for ($localY = 0; $localY -lt $frameRect.Height; $localY++) {
				for ($localX = 0; $localX -lt $frameRect.Width; $localX++) {
					$index = $localY * $frameRect.Width + $localX
					if ($frameAlpha[$index] -ne 0) { continue }
					$neighborAlpha = 0
					foreach ($offset in @(@(-1, 0), @(1, 0), @(0, -1), @(0, 1), @(-1, 1), @(1, 1))) {
						$nx = $localX + $offset[0]
						$ny = $localY + $offset[1]
						if ($nx -lt 0 -or $nx -ge $frameRect.Width -or $ny -lt 0 -or $ny -ge $frameRect.Height) { continue }
						$neighborAlpha = [Math]::Max($neighborAlpha, $frameAlpha[$ny * $frameRect.Width + $nx])
					}
					if ($neighborAlpha -ge 80) {
						$gutterAlpha = [Math]::Min(72, [int]([Math]::Round($neighborAlpha * 0.30)))
						$dds.Bitmap.SetPixel($frameRect.Left + $localX, $frameRect.Top + $localY, [Drawing.Color]::FromArgb($gutterAlpha, 0, 0, 0))
					}
				}
			}

			Export-UncompressedDds -OriginalBytes $dds.Bytes -Bitmap $dds.Bitmap -Path $path
			Write-Output "Updated $path ($($target.Width)x$($target.Height), bottom-aligned)"
		}
		finally {
			$dds.Bitmap.Dispose()
		}
	}
}
finally {
	$source.Dispose()
}
