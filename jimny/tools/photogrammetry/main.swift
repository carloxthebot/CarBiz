// Photogrammetry on this Mac: a folder of overlapping photos of one part in,
// a textured USDZ model out, using Apple's RealityKit Object Capture (free,
// runs locally on Apple Silicon).
//
//   swiftc -O -o photogrammetry main.swift
//   ./photogrammetry <photos-folder> <out.usdz> [preview|reduced|medium|full|raw]
//
// Then convert for the web:  Blender -b -P ../../blender/usdz_to_glb.py -- out.usdz out.glb
import Foundation
import RealityKit

let args = CommandLine.arguments
guard args.count >= 3 else {
    print("usage: photogrammetry <photos-folder> <out.usdz> [preview|reduced|medium|full|raw]")
    exit(2)
}
let input = URL(fileURLWithPath: args[1], isDirectory: true)
let output = URL(fileURLWithPath: args[2])
let detailName = args.count > 3 ? args[3] : "medium"
let noMask = args.contains("nomask")          // whole scenes (a car in a garage) must not be masked
let detail: PhotogrammetrySession.Request.Detail = {
    switch detailName {
    case "preview": return .preview
    case "reduced": return .reduced
    case "full": return .full
    case "raw": return .raw
    default: return .medium
    }
}()

guard PhotogrammetrySession.isSupported else {
    print("photogrammetry is not supported on this machine")
    exit(1)
}

var config = PhotogrammetrySession.Configuration()
config.featureSensitivity = .high
config.sampleOrdering = .unordered
config.isObjectMaskingEnabled = !noMask

let session: PhotogrammetrySession
do {
    session = try PhotogrammetrySession(input: input, configuration: config)
} catch {
    print("cannot open session: \(error)")
    exit(1)
}

let group = DispatchGroup()
group.enter()
Task {
    do {
        for try await event in session.outputs {
            switch event {
            case .requestProgress(_, let fraction):
                print(String(format: "progress %.0f%%", fraction * 100))
            case .requestComplete(_, let result):
                if case .modelFile(let url) = result { print("wrote \(url.path)") }
            case .requestError(_, let err):
                print("error: \(err)")
            case .processingComplete:
                group.leave()
            case .inputComplete:
                print("photos read")
            case .invalidSample(let id, let reason):
                print("skipped photo \(id): \(reason)")
            default:
                break
            }
        }
    } catch {
        print("failed: \(error)")
        group.leave()
    }
}
do {
    try session.process(requests: [.modelFile(url: output, detail: detail)])
} catch {
    print("cannot start: \(error)")
    exit(1)
}
group.wait()
