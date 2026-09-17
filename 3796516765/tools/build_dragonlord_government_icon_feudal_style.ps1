param(
	[string]$OutputPng = (Join-Path $PSScriptRoot '..\gfx\interface\icons\government_types\dragonlord_oligarchy_government.png')
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

function Add-Polygon([Drawing.Graphics]$Graphics, [Drawing.Point[]]$Points, [Drawing.Color]$Fill, [Drawing.Color]$Outline) {
	$path = [Drawing.Drawing2D.GraphicsPath]::new()
	try {
		$path.AddPolygon($Points)
		$Graphics.FillPath([Drawing.SolidBrush]::new($Fill), $path)
		$Graphics.DrawPath([Drawing.Pen]::new($Outline, 9), $path)
	}
	finally { $path.Dispose() }
}

$full = [Drawing.Bitmap]::new(280, 280, [Drawing.Imaging.PixelFormat]::Format32bppArgb)
try {
	$g = [Drawing.Graphics]::FromImage($full)
	try {
		$g.Clear([Drawing.Color]::Transparent)
		$g.SmoothingMode = [Drawing.Drawing2D.SmoothingMode]::AntiAlias
		$g.PixelOffsetMode = [Drawing.Drawing2D.PixelOffsetMode]::HighQuality

		# Same compact 70x70-icon silhouette as vanilla feudal_government:
		# low iron circlet, deep black gutter, silver upper rim and gold lower teeth.
		$outer = [Drawing.Rectangle]::new(42, 109, 196, 91)
		$g.DrawEllipse([Drawing.Pen]::new([Drawing.Color]::FromArgb(250, 0, 0, 0), 22), $outer)

		foreach ($tip in @(
			@( [Drawing.Point]::new(69,139), [Drawing.Point]::new(88,87), [Drawing.Point]::new(111,132) ),
			@( [Drawing.Point]::new(112,132), [Drawing.Point]::new(140,66), [Drawing.Point]::new(168,132) ),
			@( [Drawing.Point]::new(169,132), [Drawing.Point]::new(192,87), [Drawing.Point]::new(211,139) )
		)) {
			Add-Polygon $g $tip ([Drawing.Color]::FromArgb(255, 45, 51, 63)) ([Drawing.Color]::FromArgb(250, 3, 4, 7))
			$g.DrawLine([Drawing.Pen]::new([Drawing.Color]::FromArgb(225, 194, 205, 218), 5), $tip[0], $tip[1])
		}

		$steel = [Drawing.Drawing2D.LinearGradientBrush]::new([Drawing.Point]::new(0,112), [Drawing.Point]::new(0,199), [Drawing.Color]::FromArgb(255,95,104,118), [Drawing.Color]::FromArgb(255,19,22,28))
		$g.FillEllipse($steel, [Drawing.Rectangle]::new(48,116,184,78))
		$steel.Dispose()
		$g.DrawArc([Drawing.Pen]::new([Drawing.Color]::FromArgb(255,224,232,238),10), [Drawing.Rectangle]::new(53,116,174,61), 188,164)
		$g.DrawArc([Drawing.Pen]::new([Drawing.Color]::FromArgb(210,109,122,140),5), [Drawing.Rectangle]::new(58,124,164,60), 188,164)
		$g.DrawArc([Drawing.Pen]::new([Drawing.Color]::FromArgb(255,3,4,6),10), [Drawing.Rectangle]::new(53,125,174,74), 8,164)

		foreach ($x in 70,102,140,178,210) {
			$tooth = @( [Drawing.Point]::new($x-11,170), [Drawing.Point]::new($x+11,170), [Drawing.Point]::new($x,196) )
			Add-Polygon $g $tooth ([Drawing.Color]::FromArgb(255,207,167,92)) ([Drawing.Color]::FromArgb(245,47,28,12))
		}

		$g.FillEllipse([Drawing.SolidBrush]::new([Drawing.Color]::FromArgb(255,5,3,9)), [Drawing.Rectangle]::new(122,125,36,36))
		$gem = [Drawing.Drawing2D.LinearGradientBrush]::new([Drawing.Point]::new(130,129), [Drawing.Point]::new(151,155), [Drawing.Color]::FromArgb(255,222,135,249), [Drawing.Color]::FromArgb(255,60,17,96))
		$g.FillEllipse($gem, [Drawing.Rectangle]::new(130,130,21,23)); $gem.Dispose()
		$g.DrawEllipse([Drawing.Pen]::new([Drawing.Color]::FromArgb(245,236,199,250),3), [Drawing.Rectangle]::new(130,130,21,23))
		$g.DrawEllipse([Drawing.Pen]::new([Drawing.Color]::FromArgb(210,0,0,0),8), [Drawing.Rectangle]::new(36,103,208,101))
	}
	finally { $g.Dispose() }

	$icon = [Drawing.Bitmap]::new(28,28,[Drawing.Imaging.PixelFormat]::Format32bppArgb)
	try {
		$g = [Drawing.Graphics]::FromImage($icon)
		try {
			$g.InterpolationMode = [Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
			$g.PixelOffsetMode = [Drawing.Drawing2D.PixelOffsetMode]::HighQuality
			$g.DrawImage($full,[Drawing.Rectangle]::new(0,0,28,28))
		}
		finally { $g.Dispose() }
		$icon.Save($OutputPng,[Drawing.Imaging.ImageFormat]::Png)
	}
	finally { $icon.Dispose() }
}
finally { $full.Dispose() }

Write-Output "Created $OutputPng"
