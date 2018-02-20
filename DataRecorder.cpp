/*
 * DataRecorder.cpp
 *
 *  Created on: Feb 18, 2018
 *      Author: jguillaumes
 */

#include "DataRecorder.h"


DataRecorder::DataRecorder(int itemSize, int cspin1, int cspin2) {
	static SPISRAM ram1 = SPISRAM(&SPI,1024,cspin1);
	static SPISRAM ram2 = SPISRAM(&SPI,1024,cspin2);
	_chip1 = &ram1;
	_chip2 = &ram2;
	_header.itemSize = itemSize;
	_lastError = OK;
	_capacity = (_chip1->getSize() + _chip2->getSize() - sizeof(_header))
			/ (_header.itemSize + sizeof(uint64_t));
}

DataRecorder::~DataRecorder() {
}

bool DataRecorder::begin() {
	bool outcome = false;

	outcome = _chip1->begin(SPISRAM::SEQ, 0);
	if (outcome) _chip2->begin(SPISRAM::SEQ, 0);
	if (!readHeader()) {
		if (_lastError == BADCATCHER) {
			outcome = newHeader();
		} else {
			outcome = false;
		}
	}
	return outcome;
}

void DataRecorder::initialize() {
	newHeader();
}

DataRecorder::locator_t DataRecorder::getLocator(const uint32_t address) {
	DataRecorder::locator_t theLocator = {NULL,0};

	uint32_t capacity1 = _chip1->getSize();
	if (address < capacity1) {
		theLocator.physAddress = address;
	} else {
		theLocator.chip = _chip2;
		theLocator.physAddress = address - capacity1;
	}

	return theLocator;
}

bool DataRecorder::readKey(const uint32_t addr, uint64_t &key) {
	locator_t l = getLocator(addr);
	return l.chip->read(l.physAddress, sizeof(uint64_t), (byte*) key);
}

bool DataRecorder::putKey(const uint32_t addr, const uint64_t key) {
	locator_t l = getLocator(addr);
	return l.chip->write(l.physAddress, sizeof(uint64_t), (byte* ) &key);
}

bool DataRecorder::readHeader() {
	struct dr_header theHeader;
	if (_chip1->read(0, sizeof(struct dr_header), (byte *) &theHeader)) {

		if (memcmp(theHeader.eyecatcher, DR_CATCHER, 8)) {
			_lastError = BADCATCHER;
			return false;
		} else {
			memcpy(_header.hdrVersion, theHeader.hdrVersion, 8);
			_header.itemCount = theHeader.itemCount;
			_header.itemFirst = theHeader.itemFirst;
			_header.itemLast  = theHeader.itemLast;
			_header.itemSize  = theHeader.itemSize;
			_header.keyFirst  = theHeader.keyFirst;
			_header.keyLast   = theHeader.keyLast;
			return true;
		}
	} else {
		_lastError = IOERR;
		return false;
	}
}

bool DataRecorder::writeHeader() {
	return _chip1->write(0, sizeof(struct dr_header), (byte*) &_header);
}

bool DataRecorder::newHeader() {
	memcpy(&_header.eyecatcher, DR_CATCHER, 8);
	memcpy(&_header.hdrVersion, DR_VERSION, 8);
	_header.itemCount = 0;
	_header.itemFirst = 0;
	_header.itemLast = 0;
	_header.keyFirst = 0;
	_header.keyLast = 0;
	memset(&_header.free, ' ', 16);
 	return writeHeader();
}

bool DataRecorder::addItem(struct dr_item *item) {
	uint32_t newItem;
	newItem = _header.itemLast + 1;				// Next item uses next space
	if (newItem > _capacity) {					// Does fit in space?
		newItem = 0;							// No, we'll use first slot
	}
	if (newItem <= _header.itemFirst) {			// Have we turned around?
		_header.itemFirst += 1;					// We'll overwrite lowest item
	} else {
		_header.itemCount += 1;					// Count one plus
	}
	_header.itemLast = newItem;
	uint32_t newAddress = getAddress(newItem);
	locator_t newLocator = getLocator(newAddress);
	if (newLocator.chip->write(newLocator.physAddress,
							   sizeof(item->itemKey),
							   (byte*)&item->itemKey)) {

		return newLocator.chip->write(newLocator.physAddress+sizeof(item->itemKey),
				               _header.itemSize,
						       item->itemData);
	} else {
		return false;
	}
}

bool DataRecorder::addItem(uint64_t key, byte *data) {
	struct dr_item theItem;
	theItem.itemKey = key;
	theItem.itemData = data;
	return addItem(&theItem);
}

uint32_t DataRecorder::getAddress(const uint32_t numItem) {
	uint32_t addr;

	addr = sizeof(_header) + sizeof(uint64_t) + numItem * _header.itemSize;

	return addr;
}


