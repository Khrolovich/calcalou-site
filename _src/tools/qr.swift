// Usage: swift _src/tools/qr.swift <text>  -> SVG on stdout (CoreImage CIQRCodeGenerator, correction level M)
import CoreImage
import Foundation

let text = CommandLine.arguments[1]
let filter = CIFilter(name: "CIQRCodeGenerator")!
filter.setValue(text.data(using: .utf8), forKey: "inputMessage")
filter.setValue("M", forKey: "inputCorrectionLevel")
let image = filter.outputImage!
let cg = CIContext().createCGImage(image, from: image.extent)!
let w = cg.width, h = cg.height
var pixels = [UInt8](repeating: 0, count: w * h)
let ctx = CGContext(data: &pixels, width: w, height: h, bitsPerComponent: 8, bytesPerRow: w,
                    space: CGColorSpaceCreateDeviceGray(), bitmapInfo: CGImageAlphaInfo.none.rawValue)!
ctx.draw(cg, in: CGRect(x: 0, y: 0, width: w, height: h))
var path = ""
for y in 0..<h {
    for x in 0..<w where pixels[y * w + x] < 128 { path += "M\(x) \(y)h1v1h-1z" }
}
print("<svg xmlns=\"http://www.w3.org/2000/svg\" data-text=\"\(text)\" viewBox=\"-3 -3 \(w + 6) \(h + 6)\" shape-rendering=\"crispEdges\"><rect x=\"-3\" y=\"-3\" width=\"\(w + 6)\" height=\"\(h + 6)\" fill=\"#fff\"/><path d=\"\(path)\" fill=\"#000\"/></svg>")
