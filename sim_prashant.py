import sys

f = open("DAT_ASCII_EURUSD_M1_2000_2015.csv", "r")

cur_date = None
cur_high = None
cur_low = None

oco_buy = None
oco_sell = None
oco_set = False
oco_triggered = False
oco_sold = False
oco_type = None

handle_later = False
profit = 0.00100

for line in f:
  items = line.split()
  val_date = items[0]
  val_time = items[1]
  val_open = float(items[2])
  val_high = float(items[3])
  val_low  = float(items[4])
  val_clos = float(items[5])

  # If we've moved to the next day
  if val_date != cur_date:

    if oco_triggered and not oco_sold:
      print "---NOEXEC---"

    cur_date = val_date
    cur_high = None
    cur_low = None
    oco_buy = None
    oco_sell = None
    oco_set = False
    oco_triggered = False
    oco_sold = False
    oco_type = None
    handle_later = False

  elif handle_later:
    continue

  # while we're figuring out the 3AM 10 minute candle hi and lo
  elif val_time >= "030000" and val_time <= "031000":
    cur_high = val_high if (cur_high is None or val_high > cur_high) else cur_high
    cur_low  = val_low if (cur_low is None or val_low < cur_low) else cur_low
    if val_time == "031000":
      #print "hilo for ", cur_date, " are ", cur_high, " and ", cur_low
      oco_buy = cur_high + .00010
      oco_sell = cur_low - 0.00010
      oco_set = True
      oco_triggered = False
      print cur_date, "{0:1.6f} {1:1.6f}".format(oco_sell,oco_buy),

  # Figure out when the OCO order will trigger
  elif val_time > "031000" and oco_set and not oco_triggered:
    if val_high >= oco_buy and val_low <= oco_sell:
      # oco_triggered = True
      handle_later = True
      print "OCO sell AND buy triggered in a min:", val_time
    elif val_high >= oco_buy:
      oco_triggered = True
      oco_type = "Buy"
      print "Sell", val_time,
    elif val_low <= oco_sell:
      oco_triggered = True
      oco_type = "Sell"
      print "Buy", val_time,

  # Once OCO triggered, figure out what time profit-taking limit triggers
  elif oco_set and oco_triggered and not oco_sold:
    if oco_type == "Sell":
      target_price = oco_sell - profit
      if val_low < target_price:
        print "{0:1.6f} ".format(target_price), val_time
        oco_sold = True
    elif oco_type == "Buy":
      target_price = oco_buy + profit
      if val_high > target_price:
        print "{0:1.6f} ".format(target_price), val_time
        oco_sold = True
    else:
      print "------BUG------"

