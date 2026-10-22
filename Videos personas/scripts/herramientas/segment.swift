import Foundation
import Vision
import CoreImage
import ImageIO
import UniformTypeIdentifiers

// usage: segment <inDir> <outDir>   (processes *.jpg -> same name .png grayscale mask)
let args = CommandLine.arguments
let inDir = URL(fileURLWithPath: args[1]), outDir = URL(fileURLWithPath: args[2])
try? FileManager.default.createDirectory(at: outDir, withIntermediateDirectories: true)
let files = try FileManager.default.contentsOfDirectory(atPath: inDir.path).filter { $0.hasSuffix(".jpg") }.sorted()
let request = VNGeneratePersonSegmentationRequest()
request.qualityLevel = .accurate
request.outputPixelFormat = kCVPixelFormatType_OneComponent8
let ctx = CIContext()
var n = 0
for f in files {
    let out = outDir.appendingPathComponent(f.replacingOccurrences(of: ".jpg", with: ".png"))
    if FileManager.default.fileExists(atPath: out.path) { continue }
    autoreleasepool {
        guard let src = CGImageSourceCreateWithURL(inDir.appendingPathComponent(f) as CFURL, nil),
              let img = CGImageSourceCreateImageAtIndex(src, 0, nil) else { return }
        let handler = VNImageRequestHandler(cgImage: img, options: [:])
        do { try handler.perform([request]) } catch { print("err", f, error); return }
        guard let buf = request.results?.first?.pixelBuffer else { return }
        let ci = CIImage(cvPixelBuffer: buf)
        guard let cg = ctx.createCGImage(ci, from: ci.extent),
              let dest = CGImageDestinationCreateWithURL(out as CFURL, UTType.png.identifier as CFString, 1, nil) else { return }
        CGImageDestinationAddImage(dest, cg, nil); CGImageDestinationFinalize(dest)
        n += 1
        if n % 200 == 0 { print("masks", n) }
    }
}
print("done", n)
