"""Protect the independent sensor pin contract and runtime calculation units."""
import importlib.util
from pathlib import Path
import xml.etree.ElementTree as ET
import pytest
D=Path(__file__).resolve().parents[1]/'boards/alec-sensor'
def load(name):
 spec=importlib.util.spec_from_file_location(name,D/'tools'/f'{name}.py')
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def test_exported_sensor_interface_contract():
 assert len(load('check_design').check())>=40

def test_uart_swap_is_rejected(tmp_path):
 r=ET.parse(D/'review/netlist.xml')
 for n in r.findall('.//nets/net/node'):
  if n.get('ref')=='J3' and n.get('pin') in ['1','2']:n.set('pin',{'1':'2','2':'1'}[n.get('pin')])
 p=tmp_path/'swapped.xml';r.write(p)
 with pytest.raises(AssertionError,match='radar RX'):load('check_design').check(p)

def test_bypassing_signal_isolation_is_rejected(tmp_path):
 r=ET.parse(D/'review/netlist.xml');nets=r.findall('.//nets/net')
 tx=next(n for n in nets if any(a.get('ref')=='U3' and a.get('pin')=='10' for a in n))
 ld=next(n for n in nets if any(a.get('ref')=='J3' and a.get('pin')=='2' for a in n))
 tx.extend(list(ld));r.find('nets').remove(ld)
 p=tmp_path/'bypass.xml';r.write(p)
 with pytest.raises(AssertionError,match='not directly'):load('check_design').check(p)

def test_energy_budget_uses_hours_and_wh():
 m=load('power_budget');v=m.estimate(24,energy_wh=9,efficiency=1,mcu_active_ma=0,sleep_pack_ma=0)
 assert v['days']*24==pytest.approx(9/(5*.079))
 assert m.estimate(.25)['days']>m.estimate(1)['days']>m.estimate(24)['days']


def test_bypassing_battery_fuse_is_rejected(tmp_path):
 r=ET.parse(D/'review/netlist.xml');nets=r.findall('.//nets/net')
 raw=next(n for n in nets if any(a.get('ref')=='F1' and a.get('pin')=='1' for a in n))
 fused=next(n for n in nets if any(a.get('ref')=='F1' and a.get('pin')=='2' for a in n))
 raw.extend(list(fused));r.find('nets').remove(fused)
 p=tmp_path/'fuse-bypass.xml';r.write(p)
 with pytest.raises(AssertionError,match='Fuse cannot be bypassed'):load('check_design').check(p)
