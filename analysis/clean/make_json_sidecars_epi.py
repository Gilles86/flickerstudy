import os
from bids.layout import BIDSLayout
import sys
import json
import argparse

def main(bids_dir, 
         subject=None,
         session=None):

    print(subject, session, bids_dir)
    layout = BIDSLayout(bids_dir)
    bolds = layout.get(subject=subject, 
                       session=session,
                       extensions='nii', 
                       datatype='func',
                       suffix='bold')
    
    for bold in bolds:
        print(bold)
        epi = layout.get(suffix='epi',
                         subject=subject,
                         session=session,
                         extensions='nii',
                         acquisition=bold.acquisition,
                         run=bold.run)

        print(epi)
        assert(len(epi) == 1), 'No EPI found for {}'.format(bold.path)
        epi = epi[0]

        json_d = {'PhaseEncodingDirection':'i',
                  'TotalReadoutTime':0.04, 
                  'IntendedFor':bold.path.replace('sub-{}/'.format(subject), '')}

        print(json_d)

        json_filename = epi.path.replace("nii", "json")
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

    main('/sourcedata/ds-flicker', 
         subject=args.subject,
         session=args.session)

