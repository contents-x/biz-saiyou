// 漫画のPDFを1ページずつPNGにする（macOS 標準の PDFKit を使うので追加インストール不要）
// 実行: swift tools/sample-lp/pdf2png.swift <PDF> <出力フォルダ> <倍率>   例: 倍率 1.8 → 810pt 幅のページが 1458px
// 出力は <出力フォルダ>/p01.png〜。白紙のページ（例: アソビシステム様 A案の9ページ目）もそのまま書き出されるので、目で確認して除く
import Foundation
import PDFKit
import AppKit
let args = CommandLine.arguments
let url = URL(fileURLWithPath: args[1])
let outDir = args[2]
let scale = CGFloat(Double(args.count > 3 ? args[3] : "1") ?? 1)
guard let doc = PDFDocument(url: url) else { print("open fail"); exit(1) }
print("pages:", doc.pageCount)
for i in 0..<doc.pageCount {
  guard let page = doc.page(at: i) else { continue }
  let b = page.bounds(for: .mediaBox)
  let w = Int(b.width * scale), h = Int(b.height * scale)
  print("page", i+1, b.width, b.height)
  let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: w, pixelsHigh: h, bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
  NSGraphicsContext.saveGraphicsState()
  let ctx = NSGraphicsContext(bitmapImageRep: rep)!
  NSGraphicsContext.current = ctx
  let cg = ctx.cgContext
  cg.setFillColor(NSColor.white.cgColor); cg.fill(CGRect(x:0,y:0,width:w,height:h))
  cg.scaleBy(x: scale, y: scale)
  page.draw(with: .mediaBox, to: cg)
  NSGraphicsContext.restoreGraphicsState()
  let data = rep.representation(using: .png, properties: [:])!
  try! data.write(to: URL(fileURLWithPath: String(format: "%@/p%02d.png", outDir, i+1)))
}
