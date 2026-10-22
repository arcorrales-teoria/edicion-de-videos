import Foundation
import Vision
import ImageIO
// usage: face <dir of NNNNN.jpg> -> prints "index x y w h" (normalized, top-left origin) of the largest face per image
let dir = URL(fileURLWithPath: CommandLine.arguments[1])
let files = try FileManager.default.contentsOfDirectory(atPath: dir.path).filter { $0.hasSuffix(".jpg") }.sorted()
let req = VNDetectFaceRectanglesRequest()
for f in files {
    autoreleasepool {
        guard let src = CGImageSourceCreateWithURL(dir.appendingPathComponent(f) as CFURL, nil),
              let img = CGImageSourceCreateImageAtIndex(src, 0, nil) else { return }
        try? VNImageRequestHandler(cgImage: img, options: [:]).perform([req])
        let idx = f.replacingOccurrences(of: ".jpg", with: "")
        if let best = (req.results ?? []).max(by: { $0.boundingBox.width * $0.boundingBox.height < $1.boundingBox.width * $1.boundingBox.height }) {
            let b = best.boundingBox
            print("\(idx) \(b.origin.x) \(1 - b.origin.y - b.height) \(b.width) \(b.height)")
        } else { print("\(idx) nan nan nan nan") }
    }
}
