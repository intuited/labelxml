"""Uses the lxml package to scrape data from the .odt labels file."""
import argparse
from lxml import etree

def draw_frames(root):
    return root.xpath('//draw:frame', namespaces=root.nsmap)

def product_names(root):
    return root.xpath('//text:p[@text:style-name="P10"]', namespaces=root.nsmap)

def product_prices(root):
    return root.xpath('//text:p[@text:style-name="P9"]', namespaces=root.nsmap)

sample_page = """\
    <draw:frame draw:style-name="fr1" draw:name="Frame58" text:anchor-type="page" text:anchor-page-number="115" svg:x="0.799cm"
    svg:y="4.542cm" svg:width="8.52cm" draw:z-index="57">
      <draw:text-box fo:min-height="3.692cm">
        <table:table table:name="Table58" table:style-name="Table58">
          <table:table-column table:style-name="Table58.A" />
          <table:table-column table:style-name="Table58.B" />
          <table:table-column table:style-name="Table58.C" />
          <table:table-row table:style-name="Table58.1">
            <table:table-cell table:style-name="Table58.A1" table:number-columns-spanned="3" office:value-type="string">
              <text:p text:style-name="P3">2385 Agricola St., Halifax, Nova Scotia 
              <text:s text:c="32" />(902) 446-3301</text:p>
              <text:p text:style-name="P4">The Grainery Food Co-op</text:p>
              <text:p text:style-name="P3">also open Saturdays at the Halifax Farmers Market 1496 Lower Water Street</text:p>
            </table:table-cell>
            <table:covered-table-cell />
            <table:covered-table-cell />
          </table:table-row>
          <table:table-row table:style-name="Table58.2">
            <table:table-cell table:style-name="Table58.A2" table:number-columns-spanned="3" office:value-type="string">
              <text:p text:style-name="P5">Speerville Maritimes Organic 
              <text:s />Steel-Cut</text:p>
              <text:p text:style-name="P10">Scottish Oatmeal</text:p>
              <text:p text:style-name="P7">ABOUT SCOTTISH OATMEAL: Groats are stoneground to give a fine textured meal. Eaten as a
              breakfast cereal, use 1/2 cup cereal to 1 cup water, bring to a boil and simmer until desired consistency. 
              <text:s />Also used in many traditional Scottish baked goods.</text:p>
            </table:table-cell>
            <table:covered-table-cell />
            <table:covered-table-cell />
          </table:table-row>
          <table:table-row table:style-name="Table58.3">
            <table:table-cell table:style-name="Table58.A1" office:value-type="string">
              <text:p text:style-name="P2">750g</text:p>
            </table:table-cell>
            <table:table-cell table:style-name="Table58.A1" office:value-type="string">
              <text:p text:style-name="P15">
                <text:s />
              </text:p>
              <text:p text:style-name="P16">http://thegrainery.ca</text:p>
            </table:table-cell>
            <table:table-cell table:style-name="Table58.C3" office:value-type="currency" office:currency="USD" office:value="3">
              <text:p text:style-name="P9">$3.00</text:p>
            </table:table-cell>
          </table:table-row>
        </table:table>
        <text:p text:style-name="P1" />
      </draw:text-box>
    </draw:frame>
    """
