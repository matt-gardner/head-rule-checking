#!/usr/bin/env python


def main(supa_file, annotations_file, out_file):
    supa = []
    text = ''
    for line in open(supa_file):
        if line == '\n':
            if text is None:
                supa.append('')
                text = ''
            elif text == '':
                text = None
            else:
                supa.append(text)
                text = ''
            continue
        text += line
    annotated = []
    annotations_file = open(annotations_file)
    annotations_file.readline()
    for line in annotations_file:
        annotated.append(int(line.split('\t')[0]))

    out = open(out_file, 'w')
    for a in annotated:
        out.write(supa[a-1])
        out.write('\n')
    out.close()


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 4:
        print 'Usage:', sys.argv[0], '[supa] [annotations] [out]'
    main(sys.argv[1], sys.argv[2], sys.argv[3])

# vim: et sw=4 sts=4
