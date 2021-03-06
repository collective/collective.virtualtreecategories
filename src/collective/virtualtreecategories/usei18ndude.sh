#!/bin/bash 

# start with ./use18ndude.sh 

PRODUCT="collective.virtualtreecategories"

# if you want to add new language, add the language to the following list (separated by space)
# English language should be present even it is never translated
LANGUAGES='cs nl it'
for lang in $LANGUAGES; do
    mkdir -p locales/$lang/LC_MESSAGES/
    touch locales/$lang/LC_MESSAGES/$PRODUCT.po
done

/zope/i18ndude/myi18ndude.sh rebuild-pot --exclude bool_optparse.py --pot locales/$PRODUCT.pot --create $PRODUCT ./

# filter out invalid PO file headers. i18ndude sync adds them to the file, 
# but i18ntestcase fails if these headers are there

for lang in $LANGUAGES; do
    /zope/i18ndude/myi18ndude.sh sync --pot locales/$PRODUCT.pot locales/$lang/LC_MESSAGES/$PRODUCT.po
    mv locales/$lang/LC_MESSAGES/$PRODUCT.po locales/$lang/LC_MESSAGES/$PRODUCT.potmp
    grep -vE "^\"(Language|Domain).*" locales/$lang/LC_MESSAGES/$PRODUCT.potmp  >locales/$lang/LC_MESSAGES/$PRODUCT.po
    rm  locales/$lang/LC_MESSAGES/$PRODUCT.potmp
done

