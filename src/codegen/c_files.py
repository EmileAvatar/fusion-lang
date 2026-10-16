"""Files (Task 18.5.5), as C appended to the runtime prelude after raw bytes.

Paths are Fusion strings (UTF-8); on Windows they go through the wide-character file
functions, so names with accents work (plain fopen would use the old code page). Files are
read and written byte for byte - no newline translation. readText needs valid UTF-8 text
(a UTF-8 byte-order mark at the start is dropped, as C# does); binary files use
readBytes. Failures - a missing file, no permission - are run-time errors naming the file
and the reason, until error handling (Task 21) makes them catchable; check first with
fileExists. readLines is made on demand with the List code (c_collections.py).
"""

FILES_LIBRARY = r'''
// ---- Files (Task 18.5.5) - see src/codegen/c_files.py
#include <errno.h>
#ifdef _WIN32
__declspec(dllimport) int __stdcall MultiByteToWideChar(unsigned int page, unsigned long flags, const char* text, int len, wchar_t* out, int size);
__declspec(dllimport) unsigned long __stdcall GetFileAttributesW(const wchar_t* path);
#else
#include <sys/stat.h>
#endif
// A NUL-terminated copy of a path (malloc - freed by the caller)
static inline char* fusion_path_text(fusion_string path) {
    char* p = (char*)malloc((size_t)path.len + 1);
    memcpy(p, path.data, (size_t)path.len);
    p[path.len] = '\0';
    return p;
}
#ifdef _WIN32
static inline wchar_t* fusion_wide(const char* text) {
    int n = MultiByteToWideChar(65001, 0, text, -1, NULL, 0);
    wchar_t* w = (wchar_t*)malloc(sizeof(wchar_t) * (size_t)(n > 0 ? n : 1));
    if (n <= 0) { w[0] = 0; return w; }
    MultiByteToWideChar(65001, 0, text, -1, w, n);
    return w;
}
#endif
static inline FILE* fusion_open_file(fusion_string path, const char* mode, const char* what, const char* where) {
    char* p = fusion_path_text(path);
    FILE* f;
#ifdef _WIN32
    wchar_t* w = fusion_wide(p);
    wchar_t wmode[4] = {0};
    for (int i = 0; mode[i] && i < 3; i++) wmode[i] = (wchar_t)mode[i];
    f = _wfopen(w, wmode);
    free(w);
#else
    f = fopen(p, mode);
#endif
    if (!f) fusion_runtime_error(where, "%s: can't open '%s' (%s)", what, p, strerror(errno));
    free(p);
    return f;   // NULL when it can't be opened - the error is on its way
}
// The whole file in a fusion_alloc buffer with room for a final '\0'
static inline char* fusion_read_all(fusion_string path, int* len, const char* what, const char* where) {
    FILE* f = fusion_open_file(path, "rb", what, where);
    if (!f) return NULL;
    int cap = 4096, n = 0;
    char* data = (char*)fusion_alloc((size_t)cap + 1);
    size_t got;
    while ((got = fread(data + n, 1, (size_t)(cap - n), f)) > 0) {
        n += (int)got;
        if (n == cap) {
            if (cap > 1073741823) { fclose(f); fusion_dealloc(data); fusion_runtime_error(where, "%s: the file is larger than 2 GB", what); return NULL; }
            char* bigger = (char*)fusion_alloc((size_t)cap * 2 + 1);
            memcpy(bigger, data, (size_t)n);
            fusion_dealloc(data);
            data = bigger; cap *= 2;
        }
    }
    int failed = ferror(f);
    fclose(f);
    if (failed) { fusion_dealloc(data); fusion_runtime_error(where, "%s: reading failed (%s)", what, strerror(errno)); return NULL; }
    *len = n;
    return data;
}
static inline fusion_bytes fusion_readBytes(fusion_string path, const char* where) {
    int len;
    char* data = fusion_read_all(path, &len, "readBytes", where);
    if (!data) return FUSION_STR("");
    return fusion_bytes_take(data, len);
}
static inline fusion_string fusion_readText(fusion_string path, const char* where) {
    int len, skip = 0;
    char* data = fusion_read_all(path, &len, "readText", where);
    if (!data) return FUSION_STR("");
    if (len >= 3 && (unsigned char)data[0] == 0xEF && (unsigned char)data[1] == 0xBB && (unsigned char)data[2] == 0xBF) skip = 3;
    if (!fusion_utf8_valid(data + skip, len - skip)) {
        char* p = fusion_path_text(path);
        fusion_dealloc(data);
        fusion_runtime_error(where, "readText: '%s' is not valid text - use readBytes for a binary file", p);
        free(p);
        return FUSION_STR("");
    }
    if (skip) memmove(data, data + 3, (size_t)(len - 3));
    return fusion_str_take(data, len - skip);
}
static inline void fusion_write_all(fusion_string path, const char* mode, const char* data, int len, const char* what, const char* where) {
    FILE* f = fusion_open_file(path, mode, what, where);
    if (!f) return;
    size_t wrote = len > 0 ? fwrite(data, 1, (size_t)len, f) : 0;
    int closed = fclose(f);
    if ((int)wrote != len || closed != 0) {
        char* p = fusion_path_text(path);
        fusion_runtime_error(where, "%s: writing '%s' failed (%s)", what, p, strerror(errno));
        free(p);
    }
}
static inline void fusion_writeText(fusion_string path, fusion_string text, const char* where) { fusion_write_all(path, "wb", text.data, text.len, "writeText", where); }
static inline void fusion_appendText(fusion_string path, fusion_string text, const char* where) { fusion_write_all(path, "ab", text.data, text.len, "appendText", where); }
static inline void fusion_writeBytes(fusion_string path, fusion_bytes b, const char* where) { fusion_write_all(path, "wb", b.data, b.len, "writeBytes", where); }
// True for an existing file (not a folder)
static inline bool fusion_fileExists(fusion_string path) {
    char* p = fusion_path_text(path);
    bool found;
#ifdef _WIN32
    wchar_t* w = fusion_wide(p);
    unsigned long attributes = GetFileAttributesW(w);
    free(w);
    found = attributes != 0xFFFFFFFFul && !(attributes & 0x10ul);
#else
    struct stat info;
    found = stat(p, &info) == 0 && S_ISREG(info.st_mode);
#endif
    free(p);
    return found;
}
static inline void fusion_deleteFile(fusion_string path, const char* where) {
    char* p = fusion_path_text(path);
    int failed;
#ifdef _WIN32
    wchar_t* w = fusion_wide(p);
    failed = _wremove(w);
    free(w);
#else
    failed = remove(p);
#endif
    if (failed) fusion_runtime_error(where, "deleteFile: can't delete '%s' (%s)", p, strerror(errno));
    free(p);
}
'''
