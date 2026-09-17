param(
	[string]$SourcePng = (Join-Path $PSScriptRoot '..\art_source\dragonlord_crown_master_v6.png'),
	[string]$OutputPng = (Join-Path $PSScriptRoot '..\gfx\interface\icons\government_types\dragonlord_oligarchy_government.png'),
	[string]$PreviewPng = (Join-Path $PSScriptRoot '..\art_source\dragonlord_oligarchy_government_icon_preview.png')
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

$source = [Drawing.Bitmap]::FromFile((Resolve-Path $SourcePng))
try {
	# Find the visible crown, then use its central section. This keeps the
	# amethyst and the three most legible crown points at inline-icon scale.
	$minX = $source.Width; $minY = $source.Height; $maxX = -1; $maxY = -1
	for ($y = 0; $y -lt $source.Height; $y += 2) {
		for ($x = 0; $x -lt $source.Width; $x += 2) {
			if ($source.GetPixel($x, $y).A -gt 5) {
				$minX = [Math]::Min($minX, $x); $minY = [Math]::Min($minY, $y)
				$maxX = [Math]::Max($maxX, $x); $maxY = [Math]::Max($maxY, $y)
			}
		}
	}
	if ($maxX -lt 0) { throw 'The crown source contains no visible pixels.' }

	$visibleWidth = $maxX - $minX + 1
	$sourceRect = [Drawing.Rectangle]::new(
		$minX + [int]($visibleWidth * 0.16), $minY,
		[int]($visibleWidth * 0.68), $maxY - $minY + 1
	)

	$work = [Drawing.Bitmap]::new(112, 112, [Drawing.Imaging.PixelFormat]::Format32bppArgb)
	try {
		$graphics = [Drawing.Graphics]::FromImage($work)
		try {
			$graphics.Clear([Drawing.Color]::Transparent)
			$graphics.InterpolationMode = [Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
			$graphics.PixelOffsetMode = [Drawing.Drawing2D.PixelOffsetMode]::HighQuality
			# Slightly taller than the original frame so the miniature reads like
			# CK3's compact feudal-government icon, not a thin title decoration.
			$destination = [Drawing.Rectangle]::new(19, 20, 74, 64)
			$graphics.DrawImage($source, $destination, $sourceRect, [Drawing.GraphicsUnit]::Pixel)
		}
		finally { $graphics.Dispose() }

		# A narrow black groove around the silhouette creates the same recessed
		# edge that makes vanilla government icons readable on dark tooltips.
		$alpha = New-Object byte[] ($work.Width * $work.Height)
		for ($y = 0; $y -lt $work.Height; $y++) {
			for ($x = 0; $x -lt $work.Width; $x++) {
				$alpha[$y * $work.Width + $x] = $work.GetPixel($x, $y).A
			}
		}
		for ($y = 1; $y -lt $work.Height - 1; $y++) {
			for ($x = 1; $x -lt $work.Width - 1; $x++) {
				if ($alpha[$y * $work.Width + $x] -ne 0) { continue }
				$neighbor = 0
				foreach ($offset in @(@(-1, 0), @(1, 0), @(0, -1), @(0, 1), @(-1, 1), @(1, 1))) {
					$neighbor = [Math]::Max($neighbor, $alpha[($y + $offset[1]) * $work.Width + $x + $offset[0]])
				}
				if ($neighbor -ge 96) {
					$work.SetPixel($x, $y, [Drawing.Color]::FromArgb(92, 0, 0, 0))
				}
			}
		}

		$icon = [Drawing.Bitmap]::new(28, 28, [Drawing.Imaging.PixelFormat]::Format32bppArgb)
		try {
			$graphics = [Drawing.Graphics]::FromImage($icon)
			try {
				$graphics.InterpolationMode = [Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
				$graphics.PixelOffsetMode = [Drawing.Drawing2D.PixelOffsetMode]::HighQuality
				$graphics.DrawImage($work, [Drawing.Rectangle]::new(0, 0, 28, 28))
			}
			finally { $graphics.Dispose() }

			[IO.Directory]::CreateDirectory((Split-Path -Parent $OutputPng)) | Out-Null
			$icon.Save($OutputPng, [Drawing.Imaging.ImageFormat]::Png)
			$work.Save($PreviewPng, [Drawing.Imaging.ImageFormat]::Png)
			Write-Output "Updated $OutputPng"
		}
		finally { $icon.Dispose() }
	}
	finally { $work.Dispose() }
}
finally { $source.Dispose() }
