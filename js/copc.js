import * as Las from '../las/index.js';
import { Binary, Getter } from '../utils/index.js';
import { Hierarchy } from './hierarchy.js';
import { Info } from './info.js';
export const Copc = {
    create,
    loadHierarchyPage,
    loadCompressedPointDataBuffer,
    loadPointDataBuffer,
    loadPointDataView,
};
/**
 * Parse the COPC header and walk VLR and EVLR metadata.
 */
async function create(filename) {
    const getRemote = Getter.create(filename);
    // This is an optimization for the walking of VLRs - we'll grab a fixed size
    // buffer which is larger than the LAS header, and for subsequent requests
    // which fall within this buffer range, we can simply slice out the bytes
    // rather than making another remote fetch.
    const length = 65536;
    const promise = getRemote(0, length);
    async function get(begin, end) {
        if (end >= length)
            return getRemote(begin, end);
        const head = await promise;
        return head.slice(begin, end);
    }
    const header = Las.Header.parse(await get(0, Las.Constants.minHeaderLength));
    const vlrs = await Las.Vlr.walk(get, header);
    const infoVlr = Las.Vlr.find(vlrs, 'copc', 1);
    if (!infoVlr)
        throw new Error('COPC info VLR is required');
    const info = Info.parse(await Las.Vlr.fetch(get, infoVlr));
    let wkt;
    const wktVlr = Las.Vlr.find(vlrs, 'LASF_Projection', 2112);
    // There are a few corner-case possibilities here.  Although the LAS 1.4 spec
    // says that this must be a null-terminated string, some files in the wild
    // exist with a zero content-length.  We also want to consider the case of an
    // empty string which *does* include null-termination as a missing SRS.
    if (wktVlr && wktVlr.contentLength) {
        wkt = Binary.toCString(await Las.Vlr.fetch(get, wktVlr));
        if (wkt === '')
            wkt = undefined;
    }
    let eb = [];
    const ebVlr = Las.Vlr.find(vlrs, 'LASF_Spec', 4);
    if (ebVlr)
        eb = Las.ExtraBytes.parse(await Las.Vlr.fetch(get, ebVlr));
    return { header, vlrs, info, wkt, eb };
}
async function loadHierarchyPage(filename, page) {
    const get = Getter.create(filename);
    return Hierarchy.load(get, page);
}
async function loadCompressedPointDataBuffer(filename, { pointDataOffset, pointDataLength }) {
    const get = Getter.create(filename);
    return get(pointDataOffset, pointDataOffset + pointDataLength);
}
async function loadPointDataBuffer(filename, { pointDataRecordFormat, pointDataRecordLength }, node, lazPerf) {
    const compressed = await loadCompressedPointDataBuffer(filename, node);
    const { pointCount } = node;
    return Las.PointData.decompressChunk(compressed, { pointCount, pointDataRecordFormat, pointDataRecordLength }, lazPerf);
}
async function loadPointDataView(filename, copc, node, { lazPerf, include } = {}) {
    const buffer = await loadPointDataBuffer(filename, copc.header, node, lazPerf);
    return Las.View.create(buffer, copc.header, copc.eb, include);
}
