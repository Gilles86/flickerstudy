import os
from bids.layout import BIDSLayout
import sys
import json
import argparse

def main(bids_dir, 
         subject=None,
         session=None):

    print(subject, session, bids_dir)
    layout = BIDSLayout(bids_dir, absolute_paths=False)
    bolds = layout.get(subject=subject, 
                       session=session,
                       extensions='nii', 
                       datatype='func',
                       suffix='bold')
    
    for bold in bolds:
        epi = layout.get(suffix='epi',
                         subject=subject,
                         session=session,
                         extensions='nii',
                         run=bold.run)

        print(epi)
        assert(len(epi) == 1), 'No EPI found for {}'.format(bold.filename)
        epi = epi[0]

        json_d = {'PhaseEncodingDirection':'i',
                  'TotalReadoutTime':0.04, 
                  'IntendedFor':bold.filename.replace('sub-{}/'.format(subject), '')}

        print(json_d)

        json_filename = os.path.join(layout.root,
                                     epi.filename.replace("nii", "json"))
        print(json_filename)

        with open(json_filename, 'w') as f:
            json.dump(json_d, f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("subject", 
                        help="subject to process")
    parser.add_argument("session", 
                        default='*',
                        help="Session to process")
    args = parser.parse_args()

    main('/sourcedata/ds-odc', 
         subject=args.subject,
         session=args.session)

